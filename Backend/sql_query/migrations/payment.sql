CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  ride_request_id UUID NOT NULL 
    REFERENCES ride_requests(id) ON DELETE CASCADE,

  amount NUMERIC NOT NULL 
    CHECK (amount >= 0),

  payment_method TEXT NOT NULL DEFAULT 'cash' 
    CHECK (payment_method IN ('cash', 'online')),

  status TEXT NOT NULL DEFAULT 'pending' 
    CHECK (status IN ('pending', 'completed')),

  receipt_sent_at TIMESTAMP DEFAULT NULL,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);