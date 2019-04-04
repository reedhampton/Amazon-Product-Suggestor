Rails.application.routes.draw do
  root 'home#index'
  
  get 'home/index' , :as => :home
  
  #Routes for Queries
    #index
      get 'all_queries', to: 'query#index'
      get 'query', to: 'query#index'
    #new
      get 'query/new', to: 'query#new'
      post '/query', to: 'query#create'
    #Show
      get 'query/:id', to: 'query#show', :as => :query_show

end
