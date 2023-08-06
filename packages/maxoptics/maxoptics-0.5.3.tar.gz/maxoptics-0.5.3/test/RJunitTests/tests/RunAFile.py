from maxoptics import MosLibrary
cl = MosLibrary()
pr = cl.create_project_as("BAP")
pr.add("FDE")
pr.save()
pr.run("FDE")
