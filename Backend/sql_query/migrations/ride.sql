DROP TABLE IF EXISTS ride_applications;
DROP TABLE IF EXISTS rides;

CREATE TABLE rides (
    ride_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    driver_id UUID REFERENCES users(id),
    pickup TEXT NOT NULL,
    drop TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending', 'confirmed', 'ongoing', 'cancelled', 'completed')) DEFAULT 'pending',
    payment_status TEXT CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')) DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT NOW(),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    fare DECIMAL(10,2),
    rating_by_user DECIMAL(2,1),
    rating_by_driver DECIMAL(2,1),
    cancel_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE ride_applications (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ride_id UUID REFERENCES rides(ride_id) ON DELETE CASCADE,
    driver_id UUID REFERENCES users(id) NOT NULL,
    locations TEXT, -- JSON string containing driver's current location
    applied_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ride_id, driver_id)
);

-- Create indexes for better performance
CREATE INDEX idx_rides_status ON rides(status);
CREATE INDEX idx_rides_user_id ON rides(user_id);
CREATE INDEX idx_rides_driver_id ON rides(driver_id);
CREATE INDEX idx_ride_applications_ride_id ON ride_applications(ride_id);
CREATE INDEX idx_ride_applications_driver_id ON ride_applications(driver_id);