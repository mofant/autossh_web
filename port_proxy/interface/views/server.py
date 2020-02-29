from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from interface.serializer.server import ServerSerializer, ServerServiceListSerializer
from interface.models.server import Server
# Create your views here.


class ServerListView(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# class ServerDetailView(APIView):

#     def get_object(self, pk):
#         try:
#             return Snippet.objects.get(pk=pk)
#         except Snippet.DoesNotExist:
#             raise Http404

#     def get(self, request, pk):
#         server = self.get_object(pk)
#         serializer = ServerSerializer(instance=server)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         server = self.get_object(pk)
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServerDetailView(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       generics.GenericAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ServerServiceListView(mixins.ListModelMixin,
                            generics.GenericAPIView):

    queryset = Server.objects.all()
    serializer_class = ServerServiceListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
