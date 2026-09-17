"""
AI Service – detailed, personalized chatbot responses powered by Gemini.
Priority: Gemini → OpenAI → rule-based fallback.
"""
import os
from datetime import datetime, timedelta
from models import db
from models.finance import Income, Expense
from models.study import StudyLog
from models.habit import HabitLog
from services.finance_service import FinanceService
from services.study_service import StudyService
from services.habit_service import HabitService


class AIService:

    @staticmethod
    def _get_context(user):
        """Gather a rich snapshot of the user's current state."""
        fin        = FinanceService.monthly_stats(user.id)
        study      = StudyService.weekly_stats(user.id)
        habit      = HabitService.weekly_stats(user.id)
        avg_lifestyle = HabitService.avg_lifestyle_score(user.id)
        study_score   = StudyService.study_score(user.id)
        fin_score     = FinanceService.health_score(user.id)
        life_score    = round(fin_score * 0.35 + study_score * 0.35 + avg_lifestyle * 0.30, 1)
        cat_breakdown     = FinanceService.category_breakdown(user.id)
        subject_breakdown = StudyService.subject_breakdown(user.id)
        monthly_trend     = FinanceService.monthly_trend(user.id)
        study_trend       = StudyService.weekly_trend(user.id)
        habit_trend       = HabitService.weekly_trend(user.id)

        return {
            'user': user,
            'fin': fin,
            'study': study,
            'habit': habit,
            'fin_score': fin_score,
            'study_score': study_score,
            'avg_lifestyle': avg_lifestyle,
            'life_score': life_score,
            'cat_breakdown': cat_breakdown,
            'subject_breakdown': subject_breakdown,
            'monthly_trend': monthly_trend,
            'study_trend': study_trend,
            'habit_trend': habit_trend,
        }

    @staticmethod
    def _build_system_prompt(ctx) -> str:
        user = ctx['user']
        fin  = ctx['fin']
        cat  = ctx['cat_breakdown']
        subj = ctx['subject_breakdown']
        hab  = ctx['habit']
        trend = ctx['monthly_trend']

        top_cats  = ', '.join(f"{k} ₹{v:,.0f}" for k, v in list(cat.items())[:5]) if cat else 'None'
        subj_str  = ', '.join(f"{k} {v}h" for k, v in list(subj.items())[:6]) if subj else 'None'

        # Summarise monthly income/expense trend (last 3 months)
        trend_str = ''
        if trend and len(trend) >= 2:
            rows = trend[-3:]
            trend_str = ' | '.join(
                f"{r.get('month','?')}: income ₹{r.get('income',0):,.0f} expense ₹{r.get('expense',0):,.0f}"
                for r in rows
            )

        prompt = f"""You are **LifeLens AI**, an expert personal analytics assistant and life coach embedded inside the LifeLens app.

## About the user
- Name: {user.name}
- Email: {user.email}
- Education: {getattr(user, 'education_level', 'N/A')} | Current CGPA: {getattr(user, 'cgpa', 'N/A')} | Target CGPA: {getattr(user, 'target_cgpa', 'N/A')}
- Monthly income target: ₹{getattr(user, 'monthly_income_goal', 0) or 0:,.0f}
- Savings goal: ₹{getattr(user, 'savings_goal', 0) or 0:,.0f}
- Sleep goal: {getattr(user, 'sleep_goal', 8)}h/night
- Exercise goal: {getattr(user, 'exercise_goal', 30)} min/day
- Daily study goal: {getattr(user, 'daily_study_hours_goal', 6)}h/day

## Financial data (this month)
- Income:   ₹{fin['income']:,.0f}
- Expenses: ₹{fin['expense']:,.0f}
- Savings:  ₹{fin['savings']:,.0f} ({fin['savings_pct']}% savings rate)
- Financial health score: {ctx['fin_score']:.0f}/100
- Spending by category: {top_cats}
- 3-month trend: {trend_str or 'Not enough data'}

## Study data (this week)
- Total hours: {ctx['study']['total_hours']}h across {ctx['study']['sessions']} sessions
- Subjects studied: {subj_str}
- Study consistency score: {ctx['study_score']:.0f}/100

## Lifestyle / Habit data (this week)
- Average sleep:       {hab['avg_sleep']}h/night  (goal: {getattr(user, 'sleep_goal', 8)}h)
- Average exercise:    {hab['avg_exercise']:.0f} min/day  (goal: {getattr(user, 'exercise_goal', 30)} min)
- Average water:       {hab.get('avg_water', 0):.1f} glasses/day
- Average screen time: {hab['avg_screen']}h/day
- Lifestyle score:     {ctx['avg_lifestyle']:.0f}/100

## Overall life score: {ctx['life_score']:.1f}/100
(Formula: 35% finance + 35% study + 30% lifestyle)

---

## How you must respond

1. **Be thorough and detailed.** Never give a one-liner. Every response must include:
   - A direct answer to the question
   - Data-backed analysis using the numbers above
   - Specific, actionable recommendations with concrete steps
   - A motivational close

2. **Use rich markdown formatting:**
   - Use `##` and `###` headings to structure your answer
   - Use bullet points and numbered lists
   - **Bold** key numbers and insights
   - Use relevant emojis to make it visually engaging

3. **Always cite actual numbers** from the user's data — never give generic advice.

4. **Tailor tone** to the topic: encouraging for study/habits, analytical for finance.

5. Keep responses between 200–500 words unless a summary is requested (then be comprehensive).
"""
        return prompt

    @staticmethod
    def answer(user, question: str) -> str:
        """Route question to Gemini → OpenAI → rule-based engine."""
        gemini_key = os.environ.get('GEMINI_API_KEY', '')
        if gemini_key:
            try:
                return AIService._gemini_answer(user, question, gemini_key)
            except Exception:
                pass

        openai_key = os.environ.get('OPENAI_API_KEY', '')
        if openai_key:
            try:
                return AIService._openai_answer(user, question, openai_key)
            except Exception:
                pass

        return AIService._rule_based_answer(user, question)

    @staticmethod
    def _gemini_answer(user, question: str, api_key: str) -> str:
        from google import genai
        from google.genai import types

        ctx = AIService._get_context(user)
        system_prompt = AIService._build_system_prompt(ctx)

        client = genai.Client(api_key=api_key)

        models_to_try = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite',
            'gemini-2.5-flash-lite',
            'gemini-2.5-flash',
        ]
        last_err = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=question,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=8192,
                        temperature=0.7,
                    )
                )
                return response.text
            except Exception as e:
                last_err = e
                continue
        raise last_err

    @staticmethod
    def _gemini_weekly_summary(user, api_key: str) -> str:
        from google import genai
        from google.genai import types

        ctx = AIService._get_context(user)
        system_prompt = AIService._build_system_prompt(ctx)

        prompt = f"""Generate a comprehensive **Weekly Life Report** for {user.name}.

Structure it with these sections:
1. ## 🏆 Overall Life Score — score + one-sentence verdict
2. ## 💰 Finance Review — income vs expenses, savings rate, top spending categories, trend analysis
3. ## 📚 Study Review — hours studied, subjects covered, consistency, vs daily goal
4. ## 🌿 Lifestyle Review — sleep, exercise, water, screen time vs goals
5. ## 🎯 Top 3 Action Items — the single most impactful improvement for each area
6. ## 💬 Motivational Close — a personalised 2-3 sentence motivational message using actual numbers

Use the user's real data. Be specific, detailed, and encouraging. Use markdown formatting with emojis."""

        client = genai.Client(api_key=api_key)
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite',
            'gemini-2.5-flash-lite',
            'gemini-2.5-flash',
        ]
        last_err = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=8192,
                        temperature=0.7,
                    )
                )
                return response.text
            except Exception as e:
                last_err = e
                continue
        raise last_err

    @staticmethod
    def _openai_answer(user, question: str, api_key: str) -> str:
        import openai
        ctx = AIService._get_context(user)
        system_prompt = AIService._build_system_prompt(ctx)
        base_url = os.environ.get('AI_INTEGRATIONS_OPENAI_BASE_URL')
        client_kwargs = {'api_key': api_key}
        if base_url:
            client_kwargs['base_url'] = base_url
        client = openai.OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': question}
            ],
            max_tokens=8192
        )
        return response.choices[0].message.content

    @staticmethod
    def _rule_based_answer(user, question: str) -> str:
        """Intelligent rule-based responses using the user's actual data."""
        ctx = AIService._get_context(user)
        q = question.lower()
        fin   = ctx['fin']
        study = ctx['study']
        habit = ctx['habit']

        # ── Finance ──────────────────────────────────────────────────
        if any(w in q for w in ['sav', 'money', 'saving', 'cash', 'spend', 'expense', 'budget']):
            if fin['income'] == 0:
                return ("## 📊 No Financial Data Yet\n\nHead to the **Finance** section to log your income "
                        "and expenses — then I can give you detailed personalized insights!")

            if 'save more' in q or 'how can i save' in q:
                top_cat = max(ctx['cat_breakdown'].items(), key=lambda x: x[1]) if ctx['cat_breakdown'] else None
                lines = [f"## 💰 How to Save More\n\n**Current savings rate: {fin['savings_pct']}%** "
                         f"(Recommended: 20%+)\n"]
                if fin['savings_pct'] < 20:
                    lines.append(f"You're ₹{fin['income']*0.20 - fin['savings']:,.0f} short of the 20% savings target.")
                if top_cat:
                    lines.append(f"\n### Top Spending Category\n- **{top_cat[0]}**: ₹{top_cat[1]:,.0f} "
                                 f"({top_cat[1]/fin['expense']*100:.1f}% of total expenses)")
                lines.append("\n### Action Plan\n1. Apply the **50/30/20 rule** — 50% needs, 30% wants, 20% savings\n"
                             f"2. Cut **{top_cat[0] if top_cat else 'discretionary'}** spending by 15%\n"
                             "3. Automate savings on payday before you spend\n"
                             f"4. Target: ₹{fin['income']*0.20:,.0f}/month in savings")
                return '\n'.join(lines)

            return (f"## 💳 Financial Snapshot\n\n"
                    f"| Metric | Amount |\n|---|---|\n"
                    f"| Income | ₹{fin['income']:,.0f} |\n"
                    f"| Expenses | ₹{fin['expense']:,.0f} |\n"
                    f"| Savings | ₹{fin['savings']:,.0f} ({fin['savings_pct']}%) |\n\n"
                    f"**Financial Health Score: {ctx['fin_score']:.0f}/100**\n\n"
                    f"Use the Finance tab to see your full category breakdown and ML predictions.")

        # ── Study ────────────────────────────────────────────────────
        if any(w in q for w in ['study', 'cgpa', 'gpa', 'grade', 'learn', 'exam', 'subject', 'academ']):
            lines = [f"## 📚 Study Analysis\n\n**This week: {study['total_hours']}h across {study['sessions']} sessions**\n",
                     f"- Daily goal: {getattr(user, 'daily_study_hours_goal', 6)}h → "
                     f"Weekly target: {getattr(user, 'daily_study_hours_goal', 6)*7}h\n",
                     f"- Study score: **{ctx['study_score']:.0f}/100**\n"]
            if ctx['subject_breakdown']:
                least = min(ctx['subject_breakdown'].items(), key=lambda x: x[1])
                most  = max(ctx['subject_breakdown'].items(), key=lambda x: x[1])
                lines.append(f"\n### Subject Breakdown\n- Most studied: **{most[0]}** ({most[1]}h)\n"
                             f"- Least studied: **{least[0]}** ({least[1]}h) ← focus here")
            lines.append("\n### Recommendations\n1. Prioritize your weakest subjects early in the day\n"
                         "2. Use the Pomodoro technique (25 min study / 5 min break)\n"
                         "3. Log every session to track consistency")
            return '\n'.join(lines)

        # ── Habits ───────────────────────────────────────────────────
        if any(w in q for w in ['sleep', 'exercise', 'water', 'habit', 'lifestyle', 'screen', 'health', 'productive']):
            sleep_goal = getattr(user, 'sleep_goal', 8) or 8
            ex_goal    = getattr(user, 'exercise_goal', 30) or 30
            lines = [f"## 🌿 Lifestyle Analysis\n\n**Lifestyle Score: {ctx['avg_lifestyle']:.0f}/100**\n\n",
                     f"| Habit | Actual | Goal | Status |\n|---|---|---|---|\n",
                     f"| Sleep | {habit['avg_sleep']}h | {sleep_goal}h | "
                     f"{'✅' if habit['avg_sleep'] >= sleep_goal - 0.5 else '⚠️'} |\n",
                     f"| Exercise | {habit['avg_exercise']:.0f} min | {ex_goal} min | "
                     f"{'✅' if habit['avg_exercise'] >= ex_goal * 0.8 else '⚠️'} |\n",
                     f"| Screen time | {habit['avg_screen']}h | <4h | "
                     f"{'✅' if habit['avg_screen'] <= 4 else '⚠️'} |\n"]
            lines.append("\n### Top Actions\n1. Consistent sleep schedule — same bed/wake time daily\n"
                         "2. Even a 20-min walk counts as exercise\n"
                         "3. Use app timers to reduce screen time")
            return '\n'.join(lines)

        # ── Overall ───────────────────────────────────────────────────
        ls = ctx['life_score']
        verdict = "🏆 Excellent!" if ls >= 80 else ("⭐ Good progress!" if ls >= 60 else "💡 Room to grow!")
        return (f"## 🎯 Your Life Score: {ls:.1f}/100 — {verdict}\n\n"
                f"| Area | Score |\n|---|---|\n"
                f"| 💰 Finance | {ctx['fin_score']:.0f}/100 |\n"
                f"| 📚 Study | {ctx['study_score']:.0f}/100 |\n"
                f"| 🌿 Lifestyle | {ctx['avg_lifestyle']:.0f}/100 |\n\n"
                f"Ask me about any specific area for detailed recommendations!")

    @staticmethod
    def weekly_summary(user) -> str:
        """Generate a rich weekly summary — via Gemini if available."""
        gemini_key = os.environ.get('GEMINI_API_KEY', '')
        if gemini_key:
            try:
                return AIService._gemini_weekly_summary(user, gemini_key)
            except Exception:
                pass

        # Fallback: structured rule-based summary
        ctx   = AIService._get_context(user)
        fin   = ctx['fin']
        study = ctx['study']
        habit = ctx['habit']
        user  = ctx['user']

        lines = [
            f"## 📊 Weekly Life Report — {user.name}",
            f"### 🏆 Life Score: {ctx['life_score']:.1f}/100",
            "",
            "---",
            "## 💰 Finance",
            f"- **Income:** ₹{fin['income']:,.0f} | **Expenses:** ₹{fin['expense']:,.0f} | **Savings:** ₹{fin['savings']:,.0f} ({fin['savings_pct']}%)",
            f"- Financial Health Score: **{ctx['fin_score']:.0f}/100**",
        ]
        if ctx['cat_breakdown']:
            top = sorted(ctx['cat_breakdown'].items(), key=lambda x: -x[1])[:3]
            lines.append(f"- Top spending: {', '.join(f'{k} ₹{v:,.0f}' for k,v in top)}")

        lines += [
            "",
            "## 📚 Study",
            f"- **{study['total_hours']}h** studied across **{study['sessions']} sessions**",
            f"- Subjects: {', '.join(study['subjects']) or 'None logged'}",
            f"- Study Score: **{ctx['study_score']:.0f}/100**",
            "",
            "## 🌿 Lifestyle",
            f"- Sleep: **{habit['avg_sleep']}h**/night | Exercise: **{habit['avg_exercise']:.0f} min**/day | Screen: **{habit['avg_screen']}h**/day",
            f"- Lifestyle Score: **{ctx['avg_lifestyle']:.0f}/100**",
            "",
            "## 🎯 Action Items",
        ]

        if fin['savings_pct'] < 20:
            lines.append(f"- 💡 Raise savings rate from {fin['savings_pct']}% → 20% (save ₹{fin['income']*0.20 - fin['savings']:,.0f} more)")
        if study['total_hours'] < (getattr(user, 'daily_study_hours_goal', 6) or 6) * 7:
            gap = (getattr(user, 'daily_study_hours_goal', 6) or 6) * 7 - study['total_hours']
            lines.append(f"- 📖 Study {gap:.0f}h more to hit your weekly target")
        if habit['avg_sleep'] < ((getattr(user, 'sleep_goal', 8) or 8) - 1):
            lines.append(f"- 😴 Improve sleep to {getattr(user, 'sleep_goal', 8)}h/night")
        if habit['avg_exercise'] < ((getattr(user, 'exercise_goal', 30) or 30) * 0.5):
            lines.append(f"- 🏃 Exercise more — avg {habit['avg_exercise']:.0f} min vs {getattr(user, 'exercise_goal', 30)} min goal")
        if len(lines) == 22:
            lines.append("✅ Great week! Keep the momentum going.")

        return '\n'.join(lines)
