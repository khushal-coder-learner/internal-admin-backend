from sqlalchemy.orm import Query


def paginate(
    query: Query,
    *,
    page: int,
    limit: int,
):
    """
    Apply pagination to a SQLAlchemy query.
    """
    if page < 1:
        page = 1

    if limit < 1:
        limit = 10

    offset = (page - 1) * limit

    return query.offset(offset).limit(limit)
