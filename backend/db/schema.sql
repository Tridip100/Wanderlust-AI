CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    profile_picture TEXT,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    travel_style VARCHAR(50) CHECK (travel_style IN (
        'budget',
        'midrange',
        'premium',
        'luxury'
    )),
    onboarding_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);


-- 2. USER TRAVELER TYPES
-- One user can have multiple traveler types
CREATE TABLE user_traveler_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    traveler_type VARCHAR(50) NOT NULL CHECK (traveler_type IN (
        'solo',
        'couple',
        'family',
        'friends'
    ))
);


-- 3. USER INTERESTS
-- What activities the user loves
CREATE TABLE user_interests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interest VARCHAR(50) NOT NULL CHECK (interest IN (
        'trekking',
        'festivals',
        'off_road',
        'beaches',
        'spiritual',
        'hidden_places',
        'winter_snow',
        'food_local'
    ))
);


-- 4. USER TRAVEL VIBES
-- The feeling the user wants from a trip
CREATE TABLE user_travel_vibes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vibe VARCHAR(50) NOT NULL CHECK (vibe IN (
        'adventure_thrill',
        'restful_peaceful',
        'cultural_historical',
        'spiritual_religious',
        'offbeat_explorer',
        'party_nightlife',
        'food_local',
        'photography_nature'
    ))
);


-- 5. USER TRIP PREFERENCE
-- National, international or both
CREATE TABLE user_trip_preference (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trip_type VARCHAR(50) NOT NULL CHECK (trip_type IN (
        'national',
        'international',
        'both'
    ))
);


-- 6. DESTINATIONS
-- Places, cities, regions on the map
CREATE TABLE destinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    description TEXT,
    best_month_start INT CHECK (best_month_start BETWEEN 1 AND 12),
    best_month_end INT CHECK (best_month_end BETWEEN 1 AND 12),
    image_url TEXT,
    youtube_url TEXT,
    is_offbeat BOOLEAN DEFAULT FALSE,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 7. EVENTS
-- Festivals, carnivals, cultural events worldwide
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'festival',
        'carnival',
        'cultural',
        'fair',
        'spiritual',
        'food',
        'music',
        'adventure'
    )),
    description TEXT,
    popularity_score FLOAT DEFAULT 0.5,
    image_url TEXT,
    youtube_url TEXT,
    is_offbeat BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 8. TREKS
-- Foot trails worldwide
CREATE TABLE treks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    difficulty VARCHAR(50) NOT NULL CHECK (difficulty IN (
        'easy',
        'medium',
        'hard',
        'extreme'
    )),
    best_month_start INT NOT NULL CHECK (best_month_start BETWEEN 1 AND 12),
    best_month_end INT NOT NULL CHECK (best_month_end BETWEEN 1 AND 12),
    description TEXT,
    distance_km FLOAT,
    duration_days INT,
    popularity_score FLOAT DEFAULT 0.5,
    image_url TEXT,
    youtube_url TEXT,
    terrain_type VARCHAR(50) CHECK (terrain_type IN (
        'mountain',
        'desert',
        'forest',
        'snow',
        'coastal',
        'valley'
    )),
    is_offbeat BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 9. OFFROAD TRAILS
-- Jeep, 4x4, motorcycle, scooty routes
CREATE TABLE offroad_trails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL CHECK (vehicle_type IN (
        'jeep',
        'motorcycle',
        'scooty',
        '4x4'
    )),
    terrain_type VARCHAR(50) NOT NULL CHECK (terrain_type IN (
        'mountain',
        'desert',
        'forest',
        'snow',
        'coastal',
        'valley'
    )),
    difficulty VARCHAR(50) NOT NULL CHECK (difficulty IN (
        'easy',
        'medium',
        'hard',
        'extreme'
    )),
    road_condition VARCHAR(50) CHECK (road_condition IN (
        'paved',
        'unpaved',
        'rocky',
        'muddy',
        'seasonal'
    )),
    best_month_start INT NOT NULL CHECK (best_month_start BETWEEN 1 AND 12),
    best_month_end INT NOT NULL CHECK (best_month_end BETWEEN 1 AND 12),
    description TEXT,
    distance_km FLOAT,
    popularity_score FLOAT DEFAULT 0.5,
    image_url TEXT,
    youtube_url TEXT,
    is_offbeat BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 10. WISHLIST
-- User saved dream trips
CREATE TABLE wishlist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    trek_id UUID REFERENCES treks(id) ON DELETE CASCADE,
    offroad_id UUID REFERENCES offroad_trails(id) ON DELETE CASCADE,
    destination_id UUID REFERENCES destinations(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 11. TRAVEL HISTORY
-- Completed trips logged by user
CREATE TABLE travel_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    trek_id UUID REFERENCES treks(id) ON DELETE SET NULL,
    offroad_id UUID REFERENCES offroad_trails(id) ON DELETE SET NULL,
    destination_id UUID REFERENCES destinations(id) ON DELETE SET NULL,
    visited_on DATE NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    notes TEXT,
    personal_tip TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 12. ITINERARIES
-- AI generated travel plans saved per user
CREATE TABLE itineraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    trek_id UUID REFERENCES treks(id) ON DELETE SET NULL,
    offroad_id UUID REFERENCES offroad_trails(id) ON DELETE SET NULL,
    destination_id UUID REFERENCES destinations(id) ON DELETE SET NULL,
    traveler_type VARCHAR(50) NOT NULL CHECK (traveler_type IN (
        'solo',
        'couple',
        'family',
        'friends'
    )),
    travel_pace VARCHAR(50) NOT NULL CHECK (travel_pace IN (
        'slow',
        'fast',
        'flexible'
    )),
    budget_style VARCHAR(50) NOT NULL CHECK (budget_style IN (
        'backpacker',
        'midrange',
        'premium',
        'luxury'
    )),
    accommodation VARCHAR(50) CHECK (accommodation IN (
        'camping',
        'hostel',
        'budget_hotel',
        'midrange_hotel',
        'luxury_resort',
        'homestay'
    )),
    duration_days INT NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);