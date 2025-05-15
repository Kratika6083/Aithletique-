import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

class WorkoutPoseClassifier:
    def __init__(self, model_path='Pose_classifier/workout_pose_model.pkl'):
        self.model = joblib.load(model_path)

    def predict_pose(self, landmarks):
        input_data = np.array(landmarks).flatten().reshape(1, -1)
        prediction = self.model.predict(input_data)
        return prediction[0]
