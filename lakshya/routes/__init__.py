from .auth import auth_bp
from .main import main_bp
from .teleconsult import teleconsult_bp
from .referrals import referrals_bp
from .inventory import inventory_bp
from .high_risk import high_risk_bp
from .triage import triage_bp


def register_routes(app):
    """
    Register all modular blueprints and setup URL alias resolution.
    This guarantees 100% backward compatibility for template url_for(...) calls
    while organizing routes into maintainable domain modules.
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teleconsult_bp)
    app.register_blueprint(referrals_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(high_risk_bp)
    app.register_blueprint(triage_bp)

    # Automatically create endpoint aliases for short endpoint names
    # (e.g., allows url_for('login') and url_for('auth.login') to both work identically)
    for rule in list(app.url_map.iter_rules()):
        if "." in rule.endpoint:
            short_endpoint = rule.endpoint.split(".", 1)[1]
            if short_endpoint not in app.view_functions:
                app.add_url_rule(
                    rule.rule,
                    endpoint=short_endpoint,
                    view_func=app.view_functions[rule.endpoint],
                    methods=rule.methods,
                )


__all__ = [
    "register_routes",
    "auth_bp",
    "main_bp",
    "teleconsult_bp",
    "referrals_bp",
    "inventory_bp",
    "high_risk_bp",
    "triage_bp",
]

