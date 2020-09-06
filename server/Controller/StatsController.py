from flask_restful import Resource
from Manager.StatsManager import StatsManager
from Manager.PatientStatsManager import PatientStatsManager
from flask_jwt_extended import jwt_required
from flasgger import swag_from

statsManager = StatsManager()

# TO DO: Should move this over to new API structure (single patient stats have already been moved)
class AllStats(Resource):
    # Get global stats
    # GET api/stats
    @jwt_required
    @swag_from("../specifications/stats-all.yml", methods=["GET"])
    def get(self):
        stats = statsManager.put_data_together()
        return stats
