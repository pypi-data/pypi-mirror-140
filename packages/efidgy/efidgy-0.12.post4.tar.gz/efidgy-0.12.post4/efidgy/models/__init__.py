from time import sleep

from efidgy import impl

from . import idd_or


__all__ = [
    idd_or,
    # 'Computation',
    # 'Issue',
    # 'IssueStats',
    # 'IssueType',
    # 'Issues',
    # 'JobMessage',
    'JobState',
    'Member',
    'Project',
    'ProjectState',
    # 'ProjectSummary',
    'ProjectType',
    'ProjectTypeCode',
    # 'Role',
    'SharedMode',
    'Solution',
    # 'SolutionSummary',
    'UnitSystem',
]


class UnitSystem:
    METRIC = 'metric'
    IMPERIAL = 'imperial'


class ProjectTypeCode:
    IDD_OR = 'idd_or'


class SharedMode:
    PRIVATE = 'private'
    READONLY = 'readonly'
    EDITABLE = 'editable'


class ProjectState:
    IDLE = 'idle'
    COMPUTATING = 'computating'
    IMPORTING = 'importing'


class JobState:
    PENDING = 'pending'
    WORKING = 'working'
    ERROR = 'error'
    SUCCESS = 'success'


class IProjectType(impl.EfidgyModel):
    code = impl.fields.PrimaryKey()
    name = impl.fields.CharField()
    description = impl.fields.CharField()

    class Meta:
        path = '/refs/project_types'


class IMember(impl.Model):
    pk = impl.fields.PrimaryKey()
    email = impl.fields.CharField()
    first_name = impl.fields.CharField()
    last_name = impl.fields.CharField()
    role = impl.fields.CharField()


class IProject(impl.CustomerModel):
    pk = impl.fields.PrimaryKey()
    name = impl.fields.CharField()
    currency = impl.fields.CharField()
    project_type = impl.fields.ObjectField(model=IProjectType)
    shared_mode = impl.fields.CharField()
    owner = impl.fields.ObjectField(model=IMember)
    state = impl.fields.CharField()
    outdated = impl.fields.BooleanField()
    progress = impl.fields.FloatField()
    issue_stats = impl.fields.DictField()
    summary = impl.fields.DictField()

    class Meta:
        path = '/projects'

    def _get_computation_path(self):
        return '{}/{}/computation'.format(
            self._get_path(self._get_context()),
            self.pk,
        )

    def _log_messages(self, messages):
        logged_messages = getattr(self, '_logged_messages', 0)
        for i, message in enumerate(messages):
            if i < logged_messages:
                continue
            impl.module_logger.info(message['message'])
            logged_messages += 1
        self._logged_messages = logged_messages


class ISolution(impl.ProjectModel):
    pk = impl.fields.PrimaryKey()
    cost = impl.fields.FloatField()
    outdated = impl.fields.BooleanField()

    class Meta:
        path = '/solutions'


class ProjectType(impl.SyncViewMixin, IProjectType):
    pass


class Member(IMember):
    pass


class Project(impl.SyncChangeMixin, IProject):
    project_type = impl.fields.ObjectField(model=ProjectType)
    member = impl.fields.ObjectField(model=Member)

    def start_computation(self):
        c = impl.client.SyncClient(self._get_env())
        c.post(self._get_computation_path(), None)

    def stop_computation(self):
        c = impl.client.SyncClient(self._get_env())
        c.delete(self._get_computation_path())

    def wait_computation(self):
        while True:
            c = impl.client.SyncClient(self._get_env())
            response = c.get(self._get_computation_path())
            self._log_messages(response['messages'])
            if response['state'] not in [JobState.PENDING, JobState.WORKING]:
                break
            sleep(10)

    def computate(self):
        self.start_computation()
        self.wait_computation()


class Solution(impl.SyncViewMixin, ISolution):
    pass
