-- noinspection SqlNoDataSourceInspectionForFile

-- Compute the number of routes that serve each stop
SELECT
  b.stop_code,
  b.n_routes,
  stops.stop_name,
  stops.stop_lat,
  stops.stop_lon
FROM (
       SELECT
         stop_code,
         count(*) AS n_routes
       FROM (
              SELECT DISTINCT
                stop_code,
                route_short_name
              FROM transit.stop_times
                JOIN transit.stops ON stops.stop_id = stop_times.stop_id
                JOIN transit.trips ON trips.trip_id = stop_times.trip_id
                JOIN transit.routes ON routes.route_id = trips.route_id
              WHERE pickup_type = 0 AND drop_off_type = 0
            ) AS a
       GROUP BY stop_code
       ORDER BY n_routes DESC
     ) AS b
  JOIN transit.stops ON stops.stop_code = b.stop_code
ORDER BY n_routes DESC;


-- Compute the average number of buses that stop at each stop each hour on weekends and weekdays
SELECT
  d.schedule_type,
  d.stop_code,
  d.arrival_hour,
  d.avg_buses,
  stops.stop_lat,
  stops.stop_lon
FROM (
       SELECT
         schedule_type,
         stop_code,
         arrival_hour,
         avg(n_buses) AS avg_buses
       FROM (
              SELECT
                service_id,
                stop_code,
                arrival_hour,
                count(*) AS n_buses
              FROM (
                     SELECT
                       service_id,
                       stop_code,
                       hour(arrival_time) AS arrival_hour
                     FROM transit.stop_times
                       JOIN transit.trips ON trips.trip_id = stop_times.trip_id
                       JOIN transit.stops ON stops.stop_id = stop_times.stop_id
                   ) AS a
              GROUP BY service_id, stop_code, arrival_hour
            ) AS b
         JOIN (
                SELECT
                  service_id,
                  if(saturday + sunday > 0, 'weekend', 'weekday') AS schedule_type
                FROM transit.calendars
              ) AS c
           ON c.service_id = b.service_id
       GROUP BY schedule_type, stop_code, arrival_hour
     ) AS d
  JOIN transit.stops ON stops.stop_code = d.stop_code
ORDER BY avg_buses DESC;


-- Compute the average and standard deviation of the total duration (in hours) of trips on each route.
SELECT
  route_short_name,
  avg(duration) AS avg_duration,
  std(duration) AS std_duration
FROM
  (SELECT
     first_stop.trip_id,
     (last_stop.arrival_time - first_stop.arrival_time) / (60 * 60) AS duration
   FROM (
          SELECT
            trip_id,
            arrival_time
          FROM transit.stop_times
          WHERE stop_sequence = 1
        ) AS first_stop
     JOIN (
            SELECT
              trip_id,
              max(arrival_time) AS arrival_time
            FROM transit.stop_times
            GROUP BY trip_id
          ) AS last_stop
       ON first_stop.trip_id = last_stop.trip_id
  ) AS trip_durations
  JOIN transit.trips ON trips.trip_id = trip_durations.trip_id
  JOIN transit.routes ON routes.route_id = trips.route_id
GROUP BY route_short_name
ORDER BY avg_duration DESC;