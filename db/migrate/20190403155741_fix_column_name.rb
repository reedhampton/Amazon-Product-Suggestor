class FixColumnName < ActiveRecord::Migration[5.1]
  def change
    rename_column :queries, :type, :headphone_type
  end
end
