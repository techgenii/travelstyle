-- =============================================================================
-- TravelStyle AI - Initial Clothing Style Data
-- =============================================================================
-- This file populates the clothing_styles table with comprehensive style definitions
-- Categories: aesthetic, cultural_etiquette, functional
-- =============================================================================

-- Insert Fashion Aesthetic Styles
INSERT INTO public.clothing_styles (style_name, category, description)
VALUES
('Streetwear', 'aesthetic', 'Urban, edgy style with sneakers, oversized fits, bold graphics, and contemporary urban culture influences. Popularized by skateboarding and hip-hop culture.'),
('Minimalist', 'aesthetic', 'Clean lines, neutral tones, simple silhouettes, and "less is more" philosophy. Focuses on quality over quantity with timeless pieces.'),
('Bohemian', 'aesthetic', 'Flowy, relaxed, natural fabrics with earthy tones, ethnic patterns, and free-spirited aesthetic. Inspired by 1960s counterculture and global influences.'),
('Classic', 'aesthetic', 'Timeless staples like blazers, button-downs, tailored pants, and traditional silhouettes. Never goes out of style and suitable for any occasion.'),
('Trendy / Fast Fashion', 'aesthetic', 'Current season looks from mass-market brands, following the latest runway trends and social media fashion movements.'),
('Athleisure', 'aesthetic', 'Blends athletic and casual wear for stylish comfort. Combines performance fabrics with fashion-forward designs for everyday wear.'),
('Preppy', 'aesthetic', 'Collegiate style with polos, loafers, structured pieces, and traditional academic aesthetic. Clean, polished, and sophisticated.'),
('Avant-Garde', 'aesthetic', 'Artistic, fashion-forward, and unconventional silhouettes. Pushes boundaries and challenges traditional fashion norms.'),
('Glam / Chic', 'aesthetic', 'Glossy, upscale outfits for social or night events. Sophisticated, elegant, and designed to make a statement.'),
('Cottagecore', 'aesthetic', 'Romantic and vintage-inspired with floral prints, soft fabrics, and pastoral aesthetics. Celebrates rural life and nature.'),
('Y2K Revival', 'aesthetic', 'Early 2000s aesthetics with low-rise jeans, metallic tones, butterfly motifs, and nostalgic millennial fashion.'),
('Vintage / Retro', 'aesthetic', 'Era-specific looks like 70s flares, 90s windbreakers, and classic silhouettes from past decades. Timeless appeal with historical context.');

-- Insert Cultural & Etiquette Styles
INSERT INTO public.clothing_styles (style_name, category, description, region_applicability)
VALUES
('Modest', 'cultural_etiquette', 'Covers shoulders, chest, and knees; suitable for conservative regions and religious contexts. Respects cultural and religious dress codes.', '["AE", "SA", "ID", "EG", "IN", "MY", "TR"]'),
('Business Formal', 'cultural_etiquette', 'Professional suits and formalwear for executive meetings, corporate environments, and formal business occasions.', '[]'),
('Business Casual', 'cultural_etiquette', 'Polished but less formal attire suitable for office and networking. Professional yet comfortable for modern workplaces.', '[]'),
('Cultural Respectful', 'cultural_etiquette', 'Aligned with local traditions or expectations for respectful attire. Adapts to cultural norms while maintaining personal style.', '[]'),
('Temple-Appropriate', 'cultural_etiquette', 'Covered shoulders and legs, shoes removed before entry. Respects religious spaces and cultural traditions.', '["IN", "TH", "KH", "MY", "JP", "KR", "CN"]'),
('Mosque-Appropriate', 'cultural_etiquette', 'Loose clothing; women cover hair; men avoid shorts. Respects Islamic dress codes and religious practices.', '["SA", "AE", "ID", "TR", "EG", "MY", "PK"]'),
('Synagogue-Appropriate', 'cultural_etiquette', 'Modest dress; head covering for men; skirts/dresses for women. Respects Jewish religious traditions and customs.', '["IL", "US", "FR", "GB", "CA", "AU"]'),
('Church-Appropriate', 'cultural_etiquette', 'Conservative, neat clothing for Catholic or Orthodox churches. Respects Christian religious traditions and formal worship.', '["IT", "ES", "GR", "VA", "US", "CA", "BR"]'),
('Evening Elegant', 'cultural_etiquette', 'Cocktail dresses or formal suits for fine dining or events. Sophisticated attire for upscale social occasions.', '["FR", "US", "JP", "AE", "GB", "IT", "ES"]'),
('Resort Wear', 'cultural_etiquette', 'Chic summer wear appropriate for luxury or beach resorts. Elegant vacation attire for upscale destinations.', '["MX", "BS", "TH", "GR", "IT", "ES", "FR"]'),
('Festival / Creative', 'cultural_etiquette', 'Expressive, bold, and artistic attire for events or festivals. Celebrates creativity and self-expression.', '["US", "NL", "BR", "GB", "DE", "AU", "CA"]'),
('National / Regional Dress', 'cultural_etiquette', 'Optional traditional clothing for local or ceremonial occasions. Celebrates cultural heritage and local traditions.', '["JP", "DE", "IN", "KR", "NG", "MX", "TH"]');

-- Insert Functional Styles
INSERT INTO public.clothing_styles (style_name, category, description, region_applicability)
VALUES
('Hiking / Outdoor', 'functional', 'Durable, breathable outfits for outdoor activities and trekking. Performance-focused with weather protection and mobility.', '[]'),
('Rain Ready', 'functional', 'Waterproof jackets, boots, and accessories for wet climates. Practical protection against rain and moisture.', '["GB", "JP", "BR", "SG", "IN", "TH", "MY"]'),
('Snow Gear', 'functional', 'Thermals, coats, and boots for snowy or cold destinations. Insulated protection for extreme cold weather conditions.', '["CH", "CA", "US", "NO", "SE", "FI", "RU"]'),
('Beachwear', 'functional', 'Swimsuits, cover-ups, and sandals for seaside travel. Comfortable and practical for beach and water activities.', '["MX", "TH", "PH", "ES", "IT", "GR", "AU"]'),
('Layered Travel', 'functional', 'Outfits built from versatile, lightweight layers. Adaptable clothing system for changing weather and activities.', '[]'),
('Airport Friendly', 'functional', 'Comfortable and practical outfits for long-haul flights. Travel-optimized clothing for comfort during transit.', '[]'),
('Workout / Gym', 'functional', 'Performance athletic wear for exercise and fitness activities. Moisture-wicking, stretchy, and supportive clothing.', '[]'),
('Travel Tech', 'functional', 'Clothing with built-in technology features like anti-odor, quick-dry, and wrinkle-resistant properties.', '[]'),
('Sustainable / Eco', 'functional', 'Clothing made from sustainable materials and ethical production practices. Environmentally conscious fashion choices.', '[]'),
('Adaptive Fashion', 'functional', 'Clothing designed for people with disabilities or mobility challenges. Inclusive design with functional adaptations.', '[]');
