class QueryController < ApplicationController
    
  def index
    reset_session
    @queries = Query.all
  end
  
  def show
    @query = Query.find(params[:id])
  end

  def new
    @query = Query.new
  end
  
  def create
    reset_session

    @query = Query.new(input_params)
    @query.save
    
    #Construct our python call
    @python_call = "python3 lib/assets/task_3.py #{@query.bluetooth_weighting.to_s} #{@query.noise_cancelling_weighting.to_s} #{@query.base_weighting.to_s} #{@query.headphone_type} #{@query.max_price.to_s}";

    #WE NEED TO DO QUERY PROCESSING
    @python_return = `#{@python_call}`.split(/\s*,\s*/);
    @function_name = @python_return;
    #Insert dummy values until the middle portion of this controller operates
    session[:product_price] = @function_name
    session[:product_url] = "https://www.amazon.com/";
    session[:bluetooth_score] = 5;
    session[:battery_score] = 5;
    session[:noise_cancelling_score] = 5;
    session[:base_score] = 5;
    
    #Redirect all of the information back to the user
    redirect_to query_show_path(@query.id)
  end
  
  
  private
  def input_params
    params.require(:query).permit(:headphone_type, :bluetooth_weighting, :battery_weighting, :noise_cancelling_weighting, :base_weighting , :max_price)
  end
end
