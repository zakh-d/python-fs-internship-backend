from app.redis import get_redis_client
from app.schemas.quizz_schema import QuestionCompletionSchema, QuizzCompletionSchema, QuizzResultDisplaySchema, QuizzSchema
from app.services.quizz_service.exceptions import QuizzNotFound
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


async def test_get_response_from_cache_json(
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

    await quizz_service.evaluate_quizz(test_quizz, completion, owner)
    
    result = await quizz_service.get_cached_user_response_json(owner.id, test_quizz.id)
    assert QuizzResultDisplaySchema.model_validate(result)


async def test_get_response_from_cache_csv(
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

    await quizz_service.evaluate_quizz(test_quizz, completion, owner)
    
    result = await quizz_service.get_cached_user_response_csv(owner.id, test_quizz.id)
    assert result.startswith('Question,Answer,Is Correct')


async def test_raises_error_when_response_isnt_in_cache(
    quizz_service: QuizzService,
    company_and_users,
    test_quizz
):
    _, owner, _ = company_and_users

    try:
        await quizz_service.get_cached_user_response_json(owner.id, test_quizz.id)
    except QuizzNotFound as e:
        assert e.detail == 'User response not found'
    else:
        assert False
