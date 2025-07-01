CREATE TABLE driver_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  license TEXT,
  vehicle_info TEXT,
  is_approved BOOLEAN DEFAULT FALSE
);
