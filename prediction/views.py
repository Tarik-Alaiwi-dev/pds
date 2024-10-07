from django.http import JsonResponse

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import status

from .serializers import PredictionSerializer

# from .model import load_model, predict
from .models import Prediction

import os

from gradio_client import Client, handle_file

# Load the pre-trained model
# MODEL_PATH = os.path.join(os.path.dirname(__file__), 'chest_xray_model.pth')
# model = load_model(MODEL_PATH)

class PredictionListAPIView(generics.GenericAPIView):
    serializer_class = PredictionSerializer

    def get(self, request, *args, **kwargs):
        # Get the latest record by 'date' field
        latest_object = Prediction.objects.latest()
        serializer = self.get_serializer(latest_object)
        return JsonResponse(serializer.data, safe=False)

# class ImageClassificationView(generics.CreateAPIView):
#     serializer_class = PredictionSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         # Retrieve the uploaded image
#         image = serializer.validated_data['image']

#         # Preprocess and predict the class
#         prediction_result = predict(image, MODEL_PATH)

#         # Save the prediction to the database
#         prediction = Prediction.objects.create(image=image, inference=prediction_result)
#         prediction.save()

#         # Return the result
#         return Response({
#             'inference': prediction_result
#         }, status=status.HTTP_200_OK)

class ImageClassificationView(generics.CreateAPIView):
    serializer_class = PredictionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Retrieve the uploaded image
        image = serializer.validated_data['image']

        # Save the prediction to the database
        prediction = Prediction.objects.create(image=image)  # Save without inference initially

        # Retrieve the URL of the saved image
        image_url = request.build_absolute_uri(prediction.image.url)

        # Use the Gradio client to get the prediction
        client = Client("TarikKarol/pneumonia")
        result = client.predict(
            image=handle_file(image_url), 
            api_name="/predict"
        )

        # Save the inference result in the database
        prediction.inference = result  # Assuming 'result' contains the inference output
        prediction.save()

        # Return the result
        return Response({
            'inference': result
        }, status=status.HTTP_200_OK)


