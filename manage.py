
def deploy():
	"""Run deployment tasks."""
	from config import create_app,db
	from flask_migrate import upgrade,migrate,init,stamp
	from app.models import User,Videos,Watermark

	app = create_app()
	app.app_context().push()
	db.create_all()

	# migrate database to latest revision
	init()
	stamp()
	migrate()
	upgrade()
	
deploy()
	