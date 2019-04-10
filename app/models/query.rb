class Query < ApplicationRecord
    #Table Design
    #| headphone_type | bluetooth_weighting | noise_cancelling_weighting | base_weighting | max_price |
    #| string         | integer             | integer                    | integer        | integer   |
    
    #Validate the type value
    validates :headphone_type, inclusion: { in: ["In-Ear" , "Over-Ear" , "On-Ear"] }
    
    #Vvalidate that all of our weightings have a score between 0 and 5
    validates :headphone_type, presence: true
    validates :bluetooth_weighting, presence: true, numericality: {only_integer: true , greater_than_or_equal_to: 0 , less_than_or_equal_to: 5 }
    validates :noise_cancelling_weighting, presence: true, numericality: {only_integer: true , greater_than_or_equal_to: 0 , less_than_or_equal_to: 5 }
    validates :base_weighting, presence: true, numericality: {only_integer: true , greater_than_or_equal_to: 0 , less_than_or_equal_to: 5 }
    
    #Validate our max price is greater than 0
    validates :max_price, presence: true, numericality: {only_integer: true , greater_than_or_equal_to: 0}
end
