class QueryController < ApplicationController
    
  def index
    @queries = Query.all
  end

  def new
    @query = Query.new
  end
  
  def create
    @query = Query.new(input_params)
    @query.save
    redirect_to '/all_queries'
  end
  
  
  
  private
  def input_params
    params.require(:query).permit(:headphone_type, :bluetooth_weighting, :battery_weighting, :noise_cancelling_weighting, :base_weighting , :max_price)
  end
end
