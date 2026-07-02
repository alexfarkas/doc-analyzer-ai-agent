from agent_enums import Assignment, Role

from api.models.config.assignment_data import AssignmentData
from api.models.config.config_response import ConfigResponse
from api.models.config.model_data import ModelData
from api.models.config.role_data import RoleData

backend_config = ConfigResponse(
    roles=[
        RoleData(
            api_param=Role.SUMMARY_ANALYST.value,
            ui_title="Саммари аналитик",
            models=[ModelData(provider="openai", name="gpt-5-nano")],
            assignments=[
                AssignmentData(api_param=Assignment.EXEC.value, ui_title="Исполнитель"),
                AssignmentData(
                    api_param=Assignment.CORRECTOR.value, ui_title="Корректор"
                ),
                AssignmentData(api_param=Assignment.JUDGE.value, ui_title="Судья"),
                AssignmentData(
                    api_param=Assignment.POST_CORRECTOR.value, ui_title="Пост-корректор"
                ),
            ],
            max_agents=5,
        ),
        RoleData(
            api_param=Role.TECH_ANALYST.value,
            ui_title="Технический аналитик",
            models=[ModelData(provider="openai", name="gpt-5-nano")],
            assignments=[
                AssignmentData(api_param=Assignment.EXEC.value, ui_title="Исполнитель"),
                AssignmentData(
                    api_param=Assignment.CORRECTOR.value, ui_title="Корректор"
                ),
                AssignmentData(api_param=Assignment.JUDGE.value, ui_title="Судья"),
                AssignmentData(
                    api_param=Assignment.POST_CORRECTOR.value, ui_title="Пост-корректор"
                ),
            ],
            max_agents=5,
        ),
        RoleData(
            api_param=Role.CODE_REVIEWER.value,
            ui_title="Код-ревьюер",
            models=[ModelData(provider="openai", name="gpt-5-nano")],
            assignments=[
                AssignmentData(api_param=Assignment.EXEC.value, ui_title="Исполнитель"),
                AssignmentData(
                    api_param=Assignment.CORRECTOR.value, ui_title="Корректор"
                ),
                AssignmentData(api_param=Assignment.JUDGE.value, ui_title="Судья"),
                AssignmentData(
                    api_param=Assignment.POST_CORRECTOR.value, ui_title="Пост-корректор"
                ),
            ],
            max_agents=5,
        ),
        RoleData(
            api_param=Role.TEACHER.value,
            ui_title="Преподаватель",
            models=[ModelData(provider="openai", name="gpt-5-nano")],
            assignments=[
                AssignmentData(api_param=Assignment.EXEC.value, ui_title="Исполнитель"),
                AssignmentData(
                    api_param=Assignment.CORRECTOR.value, ui_title="Корректор"
                ),
                AssignmentData(api_param=Assignment.JUDGE.value, ui_title="Судья"),
                AssignmentData(
                    api_param=Assignment.POST_CORRECTOR.value, ui_title="Пост-корректор"
                ),
            ],
            max_agents=5,
        ),
    ]
)
