class CreateQueries < ActiveRecord::Migration[5.1]
  def change
    create_table :queries do |t|
      t.string :type
      t.integer :bluetooth_weighting
      t.integer :battery_weighting
      t.integer :noise_cancelling_weighting
      t.integer :base_weighting
      t.integer :max_price

      t.timestamps
    end
  end
end
