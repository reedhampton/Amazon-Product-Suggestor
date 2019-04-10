class RemoveBatteryWeighting < ActiveRecord::Migration[5.1]
  def change
    remove_column :queries, :battery_weighting
  end
end
