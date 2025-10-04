-- reserve_and_create.lua
-- KEYS[1] = trip:<trip_id>:available_seats
-- KEYS[2] = ticket:<ticket_id>
-- KEYS[3] = tickets:by_passenger:<passenger_id>
-- ARGV: ticket_id, passenger_id, trip_id, seat_number, total_price, currency, booking_status, created_at, idempotency_key

local seats = tonumber(redis.call('get', KEYS[1]) or '0')
if seats <= 0 then return {err='NO_SEATS'} end
if redis.call('exists', KEYS[2]) == 1 then return {err='TICKET_EXISTS'} end
redis.call('decr', KEYS[1])
redis.call('hmset', KEYS[2], 'ticket_id', ARGV[1], 'passenger_id', ARGV[2], 'trip_id', ARGV[3], 'seat_number', ARGV[4], 'total_price', ARGV[5], 'currency', ARGV[6], 'booking_status', ARGV[7], 'created_at', ARGV[8])
redis.call('sadd', KEYS[3], ARGV[1])
if ARGV[9] and ARGV[9] ~= '' then redis.call('set', 'idemp:'..ARGV[9], ARGV[1]) end
return {ok='OK'}
