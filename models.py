from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Website(db.Model):
    __tablename__ = 'websites'
    
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255))
    external_url = db.Column(db.String(500))
    url = db.Column(db.String(500))
    placement = db.Column(db.Text)
    is_free_announcement = db.Column(db.Boolean)
    is_paid_announcement = db.Column(db.Boolean)
    rating_text = db.Column(db.String(50))
    rating_class = db.Column(db.String(100))
    rating_tooltip = db.Column(db.Text)
    count_review = db.Column(db.Integer)
    first_moderation_at = db.Column(db.String(100))
    protocol = db.Column(db.String(10))
    domain_age = db.Column(db.String(100))
    domain_zone = db.Column(db.String(20))
    cre_type = db.Column(db.String(100))
    speed = db.Column(db.String(50))
    language = db.Column(db.String(50))
    countries = db.Column(db.String(255))
    regions = db.Column(db.String(255))
    amount_total_deals = db.Column(db.String(50))
    
    # Relationships
    badges = db.relationship('WebsiteBadge', backref='website', lazy='dynamic')
    categories = db.relationship('WebsiteCategory', backref='website', lazy='dynamic')
    contr_categories = db.relationship('WebsiteContrCategory', backref='website', lazy='dynamic')
    prices = db.relationship('WebsitePrice', backref='website', lazy='dynamic')
    seo_metrics = db.relationship('WebsiteSEOMetric', backref='website', lazy='dynamic')
    traffic = db.relationship('WebsiteTraffic', backref='website', lazy='dynamic')
    traffic_geo = db.relationship('WebsiteTrafficGeo', backref='website', lazy='dynamic')

class WebsiteBadge(db.Model):
    __tablename__ = 'website_badges'
    
    id = db.Column(db.BigInteger, primary_key=True)
    website_id = db.Column(db.BigInteger, db.ForeignKey('websites.id'))
    badge_text = db.Column(db.String(100))
    badge_tooltip = db.Column(db.Text)
    badge_class = db.Column(db.String(100))

class WebsiteCategory(db.Model):
    __tablename__ = 'website_categories'
    
    id = db.Column(db.BigInteger, primary_key=True)
    website_id = db.Column(db.BigInteger, db.ForeignKey('websites.id'))
    category_id = db.Column(db.Integer)
    category_name = db.Column(db.String(100))

class WebsiteContrCategory(db.Model):
    __tablename__ = 'website_contr_categories'
    
    id = db.Column(db.BigInteger, primary_key=True)
    website_id = db.Column(db.BigInteger, db.ForeignKey('websites.id'))
    contr_id = db.Column(db.Integer)
    contr_name = db.Column(db.String(100))

class WebsitePrice(db.Model):
    __tablename__ = 'website_prices'
    
    id = db.Column(db.BigInteger, primary_key=True)
    website_id = db.Column(db.BigInteger, db.ForeignKey('websites.id'))
    format_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    price_publication_raw = db.Column(db.Text)
    price_publication_old_raw = db.Column(db.Text)
    publication_with_contr_categories_raw = db.Column(db.Text)
    price_spelling_raw = db.Column(db.Text)
    price_publication = db.Column(db.Numeric(12, 2))
    price_publication_old = db.Column(db.Numeric(12, 2))
    publication_with_contr_categories = db.Column(db.Numeric(12, 2))
    price_spelling = db.Column(db.Numeric(12, 2))
    is_spelling_free = db.Column(db.Boolean)

class WebsiteSEOMetric(db.Model):
    __tablename__ = 'website_seo_metrics'
    
    id = db.Column(db.BigInteger, primary_key=True)
    website_id = db.Column(db.BigInteger, db.ForeignKey('websites.id'))
    ahrefs_rank_raw = db.Column(db.Text)
    ahrefs_dr_raw = db.Column(db.Text)
    ahrefs_ur_raw = db.Column(db.Text)
    ahrefs_backlinks_raw = db.Column(db.Text)
    ahrefs_refdomains_raw = db.Column(db.Text)
    ahrefs_keywords_raw = db.Column(db.Text)
    ahrefs_traffic_raw = db.Column(db.Text)
    serpstat_domain_rank_raw = db.Column(db.Text)
    serpstat_referring_domains_raw = db.Column(db.Text)
    serpstat_referring_links_raw = db.Column(db.Text)
    tf_raw = db.Column(db.Text)
    cf_raw = db.Column(db.Text)
    da_moz_raw = db.Column(db.Text)
    majestic_links_raw = db.Column(db.Text)
    majestic_ref_domains_raw = db.Column(db.Text)
    google_index_raw = db.Column(db.Text)
    tr_raw = db.Column(db.Text)
    gsc_clicks_raw = db.Column(db.Text)
    gsc_impressions_raw = db.Column(db.Text)
    ahrefs_rank = db.Column(db.Numeric(12, 2))
    ahrefs_dr = db.Column(db.Numeric(12, 2))
    ahrefs_ur = db.Column(db.Numeric(12, 2))
    ahrefs_backlinks = db.Column(db.Numeric(12, 2))
    ahrefs_refdomains = db.Column(db.Numeric(12, 2))
    ahrefs_keywords = db.Column(db.Numeric(12, 2))
    ahrefs_traffic = db.Column(db.Numeric(12, 2))
    serpstat_domain_rank = db.Column(db.Numeric(12, 2))
    serpstat_referring_domains = db.Column(db.Numeric(12, 2))
    serpstat_referring_links = db.Column(db.Numeric(12, 2))
    tf = db.Column(db.Numeric(12, 2))
    cf = db.Column(db.Numeric(12, 2))
    da_moz = db.Column(db.Numeric(12, 2))
    majestic_links = db.Column(db.Numeric(12, 2))
    majestic_ref_domains = db.Column(db.Numeric(12, 2))
    google_index = db.Column(db.Numeric(12, 2))
    tr = db.Column(db.Numeric(12, 2))
    gsc_clicks = db.Column(db.Numeric(12, 2))
    gsc_impressions = db.Column(db.Numeric(12, 2))

class WebsiteTraffic(db.Model):
    __tablename__ = 'website_traffic'
    
    id = db.Column(db.BigInteger, primary_key=True)
    website_id = db.Column(db.BigInteger, db.ForeignKey('websites.id'))
    traffic_source = db.Column(db.String(50))
    value_raw = db.Column(db.Text)
    value_clean = db.Column(db.Numeric(12, 2))

class WebsiteTrafficGeo(db.Model):
    __tablename__ = 'website_traffic_geo'
    
    id = db.Column(db.BigInteger, primary_key=True)
    website_id = db.Column(db.BigInteger, db.ForeignKey('websites.id'))
    country_name = db.Column(db.String(100))
    percent_raw = db.Column(db.Text)
    percent_clean = db.Column(db.Numeric(6, 2))