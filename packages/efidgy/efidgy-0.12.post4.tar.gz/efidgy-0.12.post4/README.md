# efidgy

Python bindings to efidgy services.

Read more at [https://efidgy.com/docs](https://efidgy.com/docs)

Sample usage:

``` sh
export EFIDGY_CUSTOMER_CODE=code  # https://console.efidgy.com/profile/company
export EFIDGY_ACCESS_TOKEN=token  # https://console.efidgy.com/profile/tokens
```

``` python
import datetime
import efidgy


project = efidgy.models.Project.create(
    name='Demo',
    currency='USD',
    project_type=efidgy.models.ProjectType(
        code=efidgy.models.ProjectTypeCode.IDD_OR,
    ),
    shared_mode=efidgy.models.SharedMode.PRIVATE,
)

store_address = '6133 Broadway Terr., Oakland, CA 94618, USA'
lat, lon = efidgy.tools.geocode(store_address)
store = efidgy.models.idd_or.Store.create(
    project=project,
    address=store_address,
    lat=lat,
    lon=lon,
    name='Delivery Inc.',
    open_time=datetime.time(8, 0),
    close_time=datetime.time(18, 0),
)

vehicle = efidgy.models.idd_or.Vehicle.create(
    project=project,
    store=store,
    name='Gary Bailey',
    fuel_consumption=11.76,
    fuel_price=3.25,
    salary_per_duration=21,
    duration_limit=datetime.timedelta(hours=9),
)

order_address = '1 Downey Pl, Oakland, CA 94610, USA'
lat, lon = efidgy.tools.geocode(order_address)
order = efidgy.models.idd_or.Order.create(
    project=project,
    store=store,
    name='#00001',
    address=order_address,
    lat=lat,
    lon=lon,
    ready_time=datetime.time(8, 0),
    delivery_time_from=datetime.time(12, 0),
    delivery_time_to=datetime.time(16, 0),
    load_duration=datetime.timedelta(minutes=1),
    unload_duration=datetime.timedelta(minutes=5),
    boxes=1,
    volume=3.53,
    weight=22.05,
)

project.computate()

solutions = efidgy.models.Solution.all(
    project=project,
)

if solutions:
    solution = solutions[0]

    vehicle = efidgy.models.idd_or.Vehicle.get(
        pk=vehicle.pk,
        project=project,
        solution=solution,
    )

    print(vehicle.name)
    if vehicle.route is not None:
        prev_schedule = None
        for schedule in vehicle.route.schedule:
            print('{at}\t{arr}\t{dep}'.format(
                at=schedule.start_point.name,
                arr=prev_schedule.arrival_time if prev_schedule else '',
                dep=schedule.departure_time,
            ))
            prev_schedule = schedule
        if prev_schedule:
            print('{at}\t{arr}\t{dep}'.format(
                at=prev_schedule.end_point.name,
                arr=prev_schedule.arrival_time,
                dep='',
            )
```
