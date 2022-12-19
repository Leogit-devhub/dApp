
  filename = path.split("/")[-1]
  response = HttpResponse()
  response['Content-Type']=''
  response['Content-Disposition'] = f"attachment; filename= {filename}"
  response['X-Sendfile']= str(os.path.join(settings.BASE_DIR, path))
  return response