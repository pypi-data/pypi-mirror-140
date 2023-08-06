from efidgy import impl


__all__ = [
    'Order',
    'OrderRoute',
    'OrderSchedule',
    'Path',
    'Point',
    'PointType',
    'Store',
    'Vehicle',
    'VehicleRoute',
    'VehicleSchedule',
]


class PointType:
    STORE = 'store'
    ORDER = 'order'


class IPoint(impl.Model):
    pk = impl.fields.PrimaryKey()
    address = impl.fields.CharField()
    enabled = impl.fields.BooleanField()
    lat = impl.fields.FloatField()
    lon = impl.fields.FloatField()
    point_type = impl.fields.CharField()


class IStore(IPoint, impl.ProjectModel):
    name = impl.fields.CharField()
    description = impl.fields.CharField()
    open_time = impl.fields.TimeField()
    close_time = impl.fields.TimeField()
    issues = impl.fields.DictField()

    class Meta:
        path = '/stores'


class IPath(impl.Model):
    pk = impl.fields.PrimaryKey()
    distance = impl.fields.FloatField()
    directions = impl.fields.CharField()


class IOrderRoute(impl.Model):
    vehicle = impl.fields.ObjectField(model='efidgy.models.idd_or.IVehicle')
    schedule = impl.fields.ListField(
        item='efidgy.models.idd_or.IOrderSchedule',
    )
    issues = impl.fields.DictField()


class IOrder(IPoint, impl.SolutionModel):
    name = impl.fields.CharField()
    description = impl.fields.CharField()
    features = impl.fields.ListField(item=impl.fields.CharField())
    boxes = impl.fields.IntegerField()
    volume = impl.fields.FloatField()
    weight = impl.fields.FloatField()
    ready_time = impl.fields.TimeField()
    store = impl.fields.ObjectField(model=IStore)
    delivery_time_from = impl.fields.TimeField()
    delivery_time_to = impl.fields.TimeField()
    load_duration = impl.fields.DurationField()
    unload_duration = impl.fields.DurationField()
    route = impl.fields.ObjectField(model=IOrderRoute)
    issues = impl.fields.DictField()

    class Meta:
        path = '/orders'


class ISchedule:
    pk = impl.fields.PrimaryKey()
    start_point = impl.fields.PolymorphObjectField(
        lookup_field='point_type',
        models={
            PointType.STORE: IStore,
            PointType.ORDER: IOrder,
        },
    )
    end_point = impl.fields.PolymorphObjectField(
        lookup_field='point_type',
        models={
            PointType.STORE: IStore,
            PointType.ORDER: IOrder,
        },
    )
    departure_time = impl.fields.TimeField()
    arrival_time = impl.fields.TimeField()
    path = impl.fields.ObjectField(model=IPath)


class IOrderSchedule(ISchedule, impl.Model):
    issues = impl.fields.DictField()


class IVehicleSchedule(ISchedule, impl.Model):
    orders = impl.fields.ListField(item=IOrder)
    issues = impl.fields.DictField()


class IVehicleRoute(impl.Model):
    schedule = impl.fields.ListField(item=IVehicleSchedule)
    distance = impl.fields.FloatField()
    distance_salary = impl.fields.FloatField()
    start_time = impl.fields.TimeField()
    duration = impl.fields.DurationField()
    duration_salary = impl.fields.FloatField()
    fuel = impl.fields.FloatField()
    fuel_cost = impl.fields.FloatField()
    issues = impl.fields.DictField()


class IVehicle(impl.SolutionModel):
    pk = impl.fields.PrimaryKey()
    name = impl.fields.CharField()
    description = impl.fields.CharField()
    enabled = impl.fields.BooleanField()
    store = impl.fields.ObjectField(model=IStore)
    features = impl.fields.ListField(item=impl.fields.CharField())
    fuel_consumption = impl.fields.FloatField()
    fuel_price = impl.fields.FloatField()
    salary_per_distance = impl.fields.FloatField()
    salary_per_duration = impl.fields.FloatField()
    boxes_limit = impl.fields.IntegerField()
    volume_limit = impl.fields.FloatField()
    weight_limit = impl.fields.FloatField()
    start_time = impl.fields.TimeField()
    end_time = impl.fields.TimeField()
    duration_limit = impl.fields.DurationField()
    route = impl.fields.ObjectField(model=IVehicleRoute)
    issues = impl.fields.DictField()

    class Meta:
        path = '/vehicles'


class Point(IPoint):
    pass


class Store(impl.SyncChangeMixin, IStore):
    pass


class Path(IPath):
    pass


class Order(impl.SyncChangeMixin, IOrder):
    store = impl.fields.ObjectField(model=Store)
    route = impl.fields.ObjectField(model='efidgy.models.idd_or.OrderRoute')


class OrderSchedule(IOrderSchedule):
    start_point = impl.fields.PolymorphObjectField(
        lookup_field='point_type',
        models={
            PointType.STORE: Store,
            PointType.ORDER: Order,
        },
    )
    end_point = impl.fields.PolymorphObjectField(
        lookup_field='point_type',
        models={
            PointType.STORE: Store,
            PointType.ORDER: Order,
        },
    )
    path = impl.fields.ObjectField(model=Path)


class VehicleSchedule(IVehicleSchedule):
    start_point = impl.fields.PolymorphObjectField(
        lookup_field='point_type',
        models={
            PointType.STORE: Store,
            PointType.ORDER: Order,
        },
    )
    end_point = impl.fields.PolymorphObjectField(
        lookup_field='point_type',
        models={
            PointType.STORE: Store,
            PointType.ORDER: Order,
        },
    )
    path = impl.fields.ObjectField(model=Path)
    orders = impl.fields.ListField(item=Order)


class OrderRoute(IOrderRoute):
    vehicle = impl.fields.ObjectField(model='efidgy.models.idd_or.Vehicle')
    schedule = impl.fields.ListField(item=OrderSchedule)


class VehicleRoute(IVehicleRoute):
    schedule = impl.fields.ListField(item=VehicleSchedule)


class Vehicle(impl.SyncChangeMixin, IVehicle):
    store = impl.fields.ObjectField(model=Store)
    route = impl.fields.ObjectField(model=VehicleRoute)
