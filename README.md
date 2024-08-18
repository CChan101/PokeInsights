gcloud builds submit --tag gcr.io/pokeinsights/pokeinsights --project=pokeinsights

gcloud run deploy --image gcr.io/pokeinsights/pokeinsights --platform managed  --project=pokeinsights --allow-unauthenticated


