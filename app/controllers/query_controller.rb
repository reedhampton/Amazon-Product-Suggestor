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
    if (@query.save)
      
      #Construct our python call
      @python_call = "python3 lib/assets/task_3.py #{@query.bluetooth_weighting.to_s} #{@query.noise_cancelling_weighting.to_s} #{@query.base_weighting.to_s} #{@query.headphone_type} #{@query.max_price.to_s}";
  
      #WE NEED TO DO QUERY PROCESSING
      @python_return = `#{@python_call}`.split(/\s*,\s*/);
      
      #Assign the returned string into the appropriate variables
      session[:bluetooth_score] = @python_return[0].gsub('"', '');
      session[:noise_cancelling_score] = @python_return[1].gsub('"', '');
      session[:base_score] = @python_return[2].gsub('"', '');
      session[:overall_score] = @python_return[3].gsub('"', '');
      session[:product_price] = @python_return[4].gsub('"', '');
      session[:product_url] = @python_return[5].gsub('"', '');
      session[:top_bt_url] = @python_return[6].gsub('"', '');
      session[:top_nc_url] = @python_return[7].gsub('"', '');
      session[:top_b_url] = @python_return[8].chomp('\n"]');
  
      
      #Stubbed Values
      #session[:bluetooth_score] = 4.93;
      #session[:noise_cancelling_score] = 4.85;
      #session[:base_score] = 4.66;
      #session[:overall_score] = 4.59;
      #session[:product_price] = 39.99;
      #session[:product_url] = "https://www.amazon.com/Bluedio-Bluetooth-Headphones-Wireless-headphones/dp/B00Q2VIW9M/ref=sr_1_30?fst=as%3Aoff&qid=1549834603&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-30";
      #session[:top_bt_url] = "https://www.amazon.com/Bluedio-Bluetooth-Headphones-Wireless-headphones/dp/B00Q2VIW9M/ref=sr_1_30?fst=as%3Aoff&qid=1549834603&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-30";
      #session[:top_nc_url] = "https://www.amazon.com/Sony-MDRZX110-BLK-Stereo-Headphones/dp/B00NJ2M33I/ref=sr_1_5?fst=as%3Aoff&qid=1549833820&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-5";
      #session[:top_b_url] = "https://www.amazon.com/Sennheiser-HD-202-II-Professional/dp/B003LPTAYI/ref=sr_1_24?crid=33TI8KZFDIR0D&keywords=sennheiser+headphone&qid=1550190636&s=electronics&sprefix=sennh%2Celectronics%2C281&sr=1-24";
      
      session[:top_bt_name] = session[:top_bt_url].split("/")[3].gsub! '-', ' ';
      session[:top_nc_name] = session[:top_nc_url].split("/")[3].gsub! '-', ' ';
      session[:top_b_name] = session[:top_b_url].split("/")[3].gsub! '-', ' ';
      session[:product_name] = session[:product_url].split("/")[3].gsub! '-', ' ';
      
      #Redirect all of the information back to the user
      redirect_to query_show_path(@query.id)
    end
  end
  
  
  private
  def input_params
    params.require(:query).permit(:headphone_type, :bluetooth_weighting, :noise_cancelling_weighting, :base_weighting , :max_price)
  end
end
