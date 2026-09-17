"""Finance feature tests."""

from tests.conftest import login


def test_add_income(client, app, user):
    login(client)
    response = client.post(
        "/finance/add-income",
        data={
            "amount": "25000",
            "source": "Internship",
            "description": "Monthly stipend",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    from models.finance import Income

    with app.app_context():
        income = Income.query.filter_by(user_id=user.id).first()
        assert income is not None
        assert income.amount == 25000
        assert income.source == "Internship"


def test_negative_income_is_not_saved(client, app, user):
    login(client)
    response = client.post(
        "/finance/add-income",
        data={"amount": "-100", "source": "Invalid"},
        follow_redirects=False,
    )

    assert response.status_code == 302

    from models.finance import Income

    with app.app_context():
        assert Income.query.filter_by(user_id=user.id).count() == 0


def test_add_expense(client, app, user):
    login(client)
    response = client.post(
        "/finance/add-expense",
        data={
            "amount": "500",
            "category": "Food",
            "description": "Lunch",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    from models.finance import Expense

    with app.app_context():
        expense = Expense.query.filter_by(user_id=user.id).first()
        assert expense is not None
        assert expense.amount == 500
        assert expense.category == "Food"
