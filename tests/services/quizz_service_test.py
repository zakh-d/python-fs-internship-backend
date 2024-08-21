from app.redis import get_redis_client
from app.schemas.quizz_schema import QuestionCompletionSchema, QuizzCompletionSchema, QuizzSchema
from app.services.quizz_service.service import QuizzService


async def test_evaluate_quizz_wrong(
    quizz_service: QuizzService,
    test_quizz: QuizzSchema,
    company_and_users
):
    completion = QuizzCompletionSchema(
        quizz_id=test_quizz.id,
        questions=[
            QuestionCompletionSchema(
                question_id=test_quizz.questions[0].id,
                answer_ids=[
                    test_quizz.questions[0].answers[0].id
                ]
            )
        ]
    )
    _, owner, _ = company_and_users

    result = await quizz_service.evaluate_quizz(test_quizz, completion, owner)
    assert result.score == 0


async def test_evaluate_quizz_correct(
    quizz_service: QuizzService,
    test_quizz: QuizzSchema,
    company_and_users
):
    completion = QuizzCompletionSchema(
        quizz_id=test_quizz.id,
        questions=[
            QuestionCompletionSchema(
                question_id=test_quizz.questions[0].id,
                answer_ids=[
                    test_quizz.questions[0].answers[1].id
                ]
            )
        ]
    )
    _, owner, _ = company_and_users

    result = await quizz_service.evaluate_quizz(test_quizz, completion, owner)
    assert result.score == 100


async def test_sending_same_answer_multiple_times_doesnt_make_difference(
    quizz_service: QuizzService,
    test_quizz: QuizzSchema,
    company_and_users
):
    completion = QuizzCompletionSchema(
        quizz_id=test_quizz.id,
        questions=[
            QuestionCompletionSchema(
                question_id=test_quizz.questions[0].id,
                answer_ids=[
                    test_quizz.questions[0].answers[1].id,
                    test_quizz.questions[0].answers[1].id,
                    test_quizz.questions[0].answers[1].id
                ]
            ),
        ]
    )
    _, owner, _ = company_and_users

    result = await quizz_service.evaluate_quizz(test_quizz, completion, owner)
    assert result.score == 100


async def test_evaluate_quizz_wrong_answer_and_correct_answers_cancel_each_other(
    quizz_service: QuizzService,
    test_quizz: QuizzSchema,
    company_and_users
):
    completion = QuizzCompletionSchema(
        quizz_id=test_quizz.id,
        questions=[
            QuestionCompletionSchema(
                question_id=test_quizz.questions[0].id,
                answer_ids=[
                    test_quizz.questions[0].answers[0].id,
                    test_quizz.questions[0].answers[1].id
                ]
            )
        ]
    )
    _, owner, _ = company_and_users

    result = await quizz_service.evaluate_quizz(test_quizz, completion, owner)
    assert result.score == 0


async def test_caching_user_response(
    quizz_service: QuizzService,
    test_quizz: QuizzSchema,
    company_and_users
):
    completion = QuizzCompletionSchema(
        quizz_id=test_quizz.id,
        questions=[
            QuestionCompletionSchema(
                question_id=test_quizz.questions[0].id,
                answer_ids=[
                    test_quizz.questions[0].answers[1].id,
                    test_quizz.questions[0].answers[1].id,
                    test_quizz.questions[0].answers[1].id
                ]
            ),
        ]
    )
    company, owner, _ = company_and_users

    await quizz_service.evaluate_quizz(test_quizz, completion, owner)
    
    redis = await get_redis_client()
    cache = await redis.get(f'answer:{owner.id}:{company.id}:{test_quizz.id}:{test_quizz.questions[0].id}:{test_quizz.questions[0].answers[1].id}')
    assert cache == b'1'
