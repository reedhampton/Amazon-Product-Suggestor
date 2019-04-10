#!/usr/bin/env python3
import sys
import requests
import json
from operator import itemgetter


# *******************************************
# *******************************************
# NAME = task_3.py

# INPUT: (as arguments)
# "In-Ear" , "On-Ear" , "Over-Ear" 
# (WILL COME IN BLUETOOTHPREF,NOISEPREF,BASSPREF,TYPE(string as above) ,PRICE(int) )
# max weight score will be 5

# OUTPUT (as comma seperated string)
# (RETURN: TOPPRODUCTBUESCORE,TOPPRODUCTNOISESCORE,TOPPRODUCTBASSSCORE,TOPPRODUCTOVERALLSCORE,TOPPRODUCTPRICE,TOPPRODURL,TOPBLUEURL,TOPNOISEURL,TOPBASSURL)
    
# *******************************************
# *******************************************



def pruneProdID(queryTypeString, prodIDURLList, queryPriceInt):
    
    # PRODUCT TYPE (prodID#)
    overEarType = [1,2,3,4,5,6,7,8,9,10,11,12,13,34,36,38,40,41,42,43,44,45]
    onEarType = [14,15,16,17,18,19,20,21,22,23,24,35,37,39]
    inEarType = [25,26,27,28,29,30,31,32,33]

    if (queryTypeString == "Over-Ear"):
        return( intersection(overEarType, priceRange(prodIDURLList, queryPriceInt) ) )
    elif (queryTypeString == "On-Ear"):
        return( intersection(onEarType, priceRange(prodIDURLList, queryPriceInt) ) )
    elif (queryTypeString == "In-Ear"):
        return( intersection(inEarType, priceRange(prodIDURLList, queryPriceInt) ) )
    else:
        print("Error: Invalid Type")
        exit(1)

def priceRange(prodIdUrlPrice,queryPrice):
    prodsInRange = []
    for prod in prodIdUrlPrice:
        if (float(prod[2]) < queryPrice):
            prodsInRange.append(prod[0])
    if (len(prodsInRange) < 1):
        print("Error: No products in this range")
        exit(1)
    return prodsInRange

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2))

def generateCurlCommand(prunedProdsList, queryString):

    prodIDCurl = "prodID:("
  
    for prodID in prunedProdsList[:-1]:
        prodIDCurl = prodIDCurl + str(prodID) + " OR "
    prodIDCurl = prodIDCurl + str(prunedProdsList[-1]) + ")"

    curlQuery = "reviewText:(" + queryString + ") AND " + prodIDCurl

    cmdToReturn = (
        ('q', curlQuery),
        ('rows', '1000'),
        ('fl', ['prodID', 'reviewStar']),
    )
    
    return(cmdToReturn)
    
def avgProdStar(solrResponse):
    star_dict = {} # key is prodID, value is (star,numberofreviewsused)
    
    starVal = 0
    for review in solrResponse['response']['docs']:
        starRev = review['reviewStar'][0]
        if (starRev == "5.0 out of 5 stars"):
            starVal = 5
        elif (starRev == "4.0 out of 5 stars"):
            starVal = 4
        elif (starRev == "3.0 out of 5 stars"):
            starVal = 3
        elif (starRev == "2.0 out of 5 stars"):
            starVal = 2
        elif (starRev == "1.0 out of 5 stars"):
            starVal = 1
        else:
            print("ERROR at PARSE JSON STAR CONVERT")
        
        prID = review['prodID'][0]
        if prID in star_dict:
            star_dict[prID] = ( (star_dict[prID][0] + starVal), star_dict[prID][1]+1 )
        else:
            star_dict[prID] = (starVal,1)
   
    totalNumReview = 1 # This makes the totalNum one higher than it is to prevent division by 0 when normalizing
    for i in star_dict:
        totalNumReview = totalNumReview + star_dict[i][1]
    # print(star_dict)
    avgStar = []
    for prod in star_dict:
        averaged = (star_dict[prod][0] / star_dict[prod][1])
        temp = (averaged * 1.2) + ( star_dict[prod][1] * (star_dict[prod][1] / totalNumReview) )
        a = (temp/totalNumReview)
        b = 5/a
        c = (b/500)
        # TODO : I AM HERE MESSING WITH THE SCORES ..
        #print(5-c)
        normalized = (5-c)
        #print((( (averaged * 1.1) + (star_dict[prod][1] * (star_dict[prod][1] / totalNumReview) ) ) / 5 ) + 3)
        #print("_-----")

        #normalized = ( ( (averaged * 1.1) + (star_dict[prod][1] * (star_dict[prod][1] / totalNumReview) ) ) / 5 ) + 3 # the 5 and 3 make so that it is no greater than 5 at the end. All middle is weight/normalizing
        avgStar.append( ( prod, normalized ) )
    # print(avgStar)

    return avgStar







def score(parsed1List, termPref1Int, parsed2List, termPref2Int, parsed3List, termPref3Int):
    # Apply scoring per unique prodID
    toReturn = []
    toReturn.append( [ (int(i[0]), (i[1]*termPref1Int) ) for i in parsed1List ] )
    toReturn.append( [ (int(i[0]), (i[1]*termPref2Int) ) for i in parsed2List ] )
    toReturn.append( [ (int(i[0]), (i[1]*termPref3Int) ) for i in parsed3List ] )
   
    return(toReturn)







def tops(termsScoreListofList,queryTerm1Pref,queryTerm2Pref,queryTerm3Pref):
    # each list is a query containing tuples of the unqiue prod id and their score
    
    highestScoreProdInQueryList = []

    for prodList in termsScoreListofList:
        highestScoreProdInQueryList.append(max(prodList,key=itemgetter(1))) # gets top prod ID in each prodList (only gets first / wont catch other tops) ........ PROB just want to have store in list in case duplicate is winner
    
    prodScoreDict = {} # dict for sum of unique prod ID scores across all lists (score, instances)
    for i in termsScoreListofList:
        for j in i:
            if j[0] in prodScoreDict:
                prodScoreDict[j[0]] = (prodScoreDict[j[0]][0]+j[1],prodScoreDict[j[0]][1]+1)
            else:
                prodScoreDict[j[0]] = (j[1],1)

    # ? : -- Attempting to normalize these I took the ( average * ( # queries appeared in / 10 ) ) ... ex) 4.5+4.0+5.0 >> 4.5 >> 4.5*0.3 >> 1.35 // vs // 5.0 >> 5.0 >> 5.0*0.1 >> 0.5 // 1.35 vs 0.5 >> 1.35 wins
    prodIdAvgScoreDict = {} # dict for average of unique prod ID scores across all lists (id, average score)
    for t in prodScoreDict:
        prodIdAvgScoreDict[t] = ( t, (prodScoreDict[t][0] / prodScoreDict[t][1]) )
        prodScoreDict[t] = ( prodIdAvgScoreDict[t][1] * (prodScoreDict[t][1] / 10) ) # Change to prodScoreDict such that it now is normalized and only contains normalized average score per unique ID



    bestProduct = prodIdAvgScoreDict[(max(prodScoreDict.items(), key=itemgetter(1))[0])] # the best product ( is the prodID ( that has the highest ( normalized average score ) ) ) // [id,overallavgscore]

    toReturn = [bestProduct[0]]
    
    noitem = False

    for lis in termsScoreListofList:
        for item in lis:
            #print(item)
            if (item[0] == bestProduct[0]):
                toReturn.append(item[1])
                noitem = True
        #print("---")
        
        # ! Error .. if best product is not included in tops list then doesnt append value for that assoicated score
        if False == noitem:
            print("error??")
        noitem = True

            
    a = 10/(bestProduct[1])
    b = (5- (a/3))
    toReturn.append(round(b,2))

    toReturn.append(highestScoreProdInQueryList[0])
    toReturn.append(highestScoreProdInQueryList[1])
    toReturn.append(highestScoreProdInQueryList[2])

    
    if(queryTerm1Pref!=-9 and queryTerm2Pref!=-9 and queryTerm3Pref!=-9 ):
        toReturn[1] = round(toReturn[1] / queryTerm1Pref,2)
        toReturn[2] = round(toReturn[2] / queryTerm2Pref,2)
        toReturn[3] = round(toReturn[3] / queryTerm3Pref,2)
        toReturn[5] = ( toReturn[5][0], round(toReturn[5][1] / queryTerm1Pref,2) )
        toReturn[6] = ( toReturn[6][0], round(toReturn[6][1] / queryTerm2Pref,2) )
        toReturn[7] = ( toReturn[7][0], round(toReturn[7][1] / queryTerm3Pref,2) )
    else:
        if(queryTerm1Pref==-9):
            toReturn[1] = 0
            toReturn[5] = ( toReturn[5][0], 0 )
        if(queryTerm2Pref==-9):
            toReturn[2] = 0
            toReturn[6] = ( toReturn[6][0], 0 )
        if(queryTerm3Pref==-9):
            toReturn[3] = 0
            toReturn[7] = ( toReturn[7][0], 0 )


    return(toReturn)
    



def toRubyString(champList,prodUrlPriceList):
    # (RETURN: TOPPRODUCTBUESCORE,TOPPRODUCTNOISESCORE,TOPPRODUCTBASSSCORE,TOPPRODUCTOVERALLSCORE,TOPPRODUCTPRICE,TOPPRODURL,TOPBLUEURL,TOPNOISEURL,TOPBASSURL)
    #print(champList[0])
    rubyString = str(champList[1]) + "," + str(champList[2]) + "," + str(champList[3]) + "," + str(champList[4]) + "," + str(prodUrlPriceList[champList[0]-1][2]) + "," + str(prodUrlPriceList[champList[0]-1][1]) + "," + str(prodUrlPriceList[champList[5][0]-1][1]) + "," + str(prodUrlPriceList[champList[6][0]-1][1]) + "," + str(prodUrlPriceList[champList[7][0]-1][1])
    return rubyString




def main():

    # *******************************************
    # KNOWN DATA THAT SHOULD HAVE BEEN IN DB
    # -------------------------------------------

    # PRODUCT ID, URL,PRICE
    prodIDUrlPrice = [ 
        (1,"https://www.amazon.com/Sony-Noise-Cancelling-Headphones-WH1000XM3/dp/B07G4MNFS1/ref=sr_1_1?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-1","348"),
        (2,"https://www.amazon.com/Bose-QuietComfort-Wireless-Headphones-Cancelling/dp/B0756CYWWD/ref=sr_1_2?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-2","349"),
        (3,"https://www.amazon.com/Cancelling-Headphones-Bluetooth-Comfortable-Cellphone/dp/B019U00D7K/ref=sr_1_3?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-3","59.99"),
        (4,"https://www.amazon.com/Mpow-Bluetooth-Headphones-Wireless-Memory-Protein/dp/B01NAJGGA2/ref=sr_1_4?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-4","34.99"),
        (5,"https://www.amazon.com/Cancelling-Headphone-Bluetooth-Headphones-Microphone/dp/B077YG22Y9/ref=sr_1_5?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-5","89.99"),
        (6,"https://www.amazon.com/TaoTronics-Cancelling-Headphones-Bluetooth-Cellphone/dp/B07L5LPSQT/ref=sr_1_6?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-6","59.99"),
        (7,"https://www.amazon.com/iJoy-Rechargeable-Wireless-Headphones-Bluetooth/dp/B01HNMTCE2/ref=sr_1_8?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-8","16.99"),
        (8,"https://www.amazon.com/Bose-SoundLink-around-ear-wireless-headphones/dp/B0117RGG8E/ref=sr_1_9?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-9","229"),
        (9,"https://www.amazon.com/Beats-Studio3-Wireless-Over-Ear-Headphones/dp/B075G56GZD/ref=sr_1_10?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-10","279.95"),
        (10,"https://www.amazon.com/Mpow-Cancelling-Headphones-Bluetooth-Noise-Cancelling/dp/B076H63ZK7/ref=sr_1_11?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-11","45.99"),
        (11,"https://www.amazon.com/Bose-QuietComfort-Acoustic-Cancelling-Headphones/dp/B00M1NEUKK/ref=sr_1_16?fst=as%3Aoff&qid=1549833817&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-16","198"),
        (12,"https://www.amazon.com/TaoTronics-Cancelling-Bluetooth-Headphones-Noise-Cancelling/dp/B075CBHN9M/ref=sr_1_26?fst=as%3Aoff&qid=1549833871&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-26","57.99"),
        (13,"https://www.amazon.com/Wireless-Bluetooth-Headphones-Comfortable-Playtime/dp/B01CZNLRLK/ref=sr_1_67?fst=as%3Aoff&qid=1549833983&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-67","46.69"),
        (14,"https://www.amazon.com/Sennheiser-RS120-Wireless-Headphones-Charging/dp/B0001FTVEK/ref=sr_1_2?fst=as%3Aoff&qid=1549833820&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-2","129"),
        (15,"https://www.amazon.com/Sony-MDRZX110-BLK-Stereo-Headphones/dp/B00NJ2M33I/ref=sr_1_5?fst=as%3Aoff&qid=1549833820&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-5","15.84"),
        (16,"https://www.amazon.com/Beats-Solo3-Wireless-Headphones-Anniversary/dp/B01LWWY3E2/ref=sr_1_6?fst=as%3Aoff&qid=1549833820&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-6&th=1","299.95"),
        (17,"https://www.amazon.com/Panasonic-Headphones-Lightweight-RP-HT21-Silver/dp/B00004T8R2/ref=sr_1_7?fst=as%3Aoff&qid=1549833820&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-7","7"),
        (18,"https://www.amazon.com/Bose-SoundLink-Bluetooth-Headphones-Microphone/dp/B074QRK6CG/ref=sr_1_15?fst=as%3Aoff&qid=1549833820&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-15","230.61"),
        (19,"https://www.amazon.com/Bluedio-Bluetooth-Headphones-Wireless-headphones/dp/B00Q2VIW9M/ref=sr_1_30?fst=as%3Aoff&qid=1549834603&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-30","39.99"),
        (20,"https://www.amazon.com/Behringer-HPX2000-Headphones-High-Definition-DJ/dp/B000IKWBC2/ref=sr_1_37?fst=as%3Aoff&qid=1549834603&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-37","29.99"),
        (21,"https://www.amazon.com/Mpow-Bluetooth-Headphones-Wireless-Foldable/dp/B06Y27HM9W/ref=sr_1_41?fst=as%3Aoff&qid=1549834603&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-41","24.99"),
        (22,"https://www.amazon.com/Sony-MDRXB650BT-Extra-Bluetooth-Headphones/dp/B01BY7ZMXC/ref=sr_1_47?fst=as%3Aoff&qid=1549834603&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-47","89"),
        (23,"https://www.amazon.com/Sennheiser-HDR120-Supplemental-Wireless-Headphone/dp/B000EBPJCO/ref=sr_1_66?fst=as%3Aoff&qid=1549834641&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-66","61.56"),
        (24,"https://www.amazon.com/Audio-Technica-ATH-ANC9-QuietPoint-Noise-Cancelling-Headphones/dp/B007KWLF5K/ref=sr_1_99?fst=as%3Aoff&qid=1549834704&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-99","107.99"),
        (25,"https://www.amazon.com/Mpow-Bluetooth-Headphones-Waterproof-Cancelling/dp/B0753GRNQZ/ref=sr_1_3?fst=as%3Aoff&qid=1549834140&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-3","19.99"),
        (26,"https://www.amazon.com/Wireless-ENACFIRE-Bluetooth-Headphones-Microphone/dp/B078WP9M4F/ref=sr_1_5?fst=as%3Aoff&qid=1549834140&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-5","45.99"),
        (27,"https://www.amazon.com/Jabra-Enabled-Wireless-Earbuds-Charging/dp/B077ZGRVRX/ref=sr_1_7?fst=as%3Aoff&qid=1549834140&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-7","151.88"),
        (28,"https://www.amazon.com/Bose-SoundSport-Truly-Wireless-Headphones/dp/B0748G1QLP/ref=sr_1_10?fst=as%3Aoff&qid=1549834140&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-10","199"),
        (29,"https://www.amazon.com/Bose-SoundSport-Wireless-Headphones-761529-0010/dp/B01L7PSJFO/ref=sr_1_12?fst=as%3Aoff&qid=1549834140&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-12","149"),
        (30,"https://www.amazon.com/Bluetooth-Headphones-Waterproof-Sweatproof-Cancelling/dp/B01G8JO5F2/ref=sr_1_14?fst=as%3Aoff&qid=1549835187&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-14","19.97"),
        (31,"https://www.amazon.com/LETSCOM-Headphones-Waterproof-Sweatproof-Cancelling/dp/B07DXQTCQL/ref=sr_1_19?fst=as%3Aoff&qid=1549835187&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-19","19.95"),
        (32,"https://www.amazon.com/Bose-SoundSport-ear-headphones-741776-0010/dp/B0117RFOEG/ref=sr_1_20?fst=as%3Aoff&qid=1549835187&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-20","59.99"),
        (33,"https://www.amazon.com/Wireless-Headphones-Bluetooth-Earphone-Isolating/dp/B07MW59JJY/ref=sr_1_3?fst=as%3Aoff&qid=1549835247&refinements=p_72%3A1248880011&rnid=1248877011&s=electronics&sr=1-3","25.99"),
        (34,"https://www.amazon.com/Audio-Technica-ATH-M50x-Professional-Monitor-Headphones/dp/B00HVLUR86/ref=sr_1_3?keywords=ath-m50x&qid=1550190035&s=electronics&sr=1-3&th=1","129"),
        (35,"https://www.amazon.com/Sennheiser-HD-202-II-Professional/dp/B003LPTAYI/ref=sr_1_24?crid=33TI8KZFDIR0D&keywords=sennheiser+headphone&qid=1550190636&s=electronics&sprefix=sennh%2Celectronics%2C281&sr=1-24","58"),
        (36,"https://www.amazon.com/Sennheiser-HD-598-Over-Ear-Headphones/dp/B0042A8CW2/ref=sr_1_10?keywords=sennheiser+hd555&qid=1550190724&s=electronics&sr=1-10","446.69"),
        (37,"https://www.amazon.com/Sony-MDRZX110-BLK-Stereo-Headphones/dp/B00NJ2M33I/ref=sr_1_5?crid=3LTC8GSHG2OY8&keywords=sony+headphones+over+ear&qid=1550191049&s=electronics&sprefix=sony+headphones%2Celectronics%2C162&sr=1-5","14.99"),
        (38,"https://www.amazon.com/Avantree-Cancelling-Wireless-Headphones-Bluetooth/dp/B07GVDZSK8/ref=sr_1_59?keywords=headphones&qid=1550191712&s=electronics&sr=1-59","66.99"),
        (39,"https://www.amazon.com/66-AUDIO-Wireless-Headphones-Cancellation/dp/B00E0GRRR4/ref=sr_1_141?keywords=headphones&qid=1550191806&s=electronics&sr=1-141","41.99"),
        (40,"https://www.amazon.com/Sennheiser-HD280PRO-Headphones-old-model/dp/B00IT0IHOY/ref=sr_1_180?keywords=headphones&qid=1550191855&s=electronics&sr=1-180&th=1","99.95"),
        (41,"https://www.amazon.com/B%C3%96HM-Wireless-Bluetooth-Headphones-Cancellation/dp/B01251KZUQ/ref=sr_1_205?keywords=headphones&qid=1550191887&s=electronics&sr=1-205","59.95"),
        (42,"https://www.amazon.com/Sony-MDRXB950BT-Extra-Bluetooth-Headphones/dp/B00MCHE38O/ref=sr_1_218?keywords=headphones&qid=1550191887&s=electronics&sr=1-218","169.95"),
        (43,"https://www.amazon.com/Sony-MDRZX300-RED-Outdoor-Headphones/dp/B004RKVXXM/ref=sr_1_219?keywords=headphones&qid=1550191913&s=electronics&sr=1-219","39.95"),
        (44,"https://www.amazon.com/Panasonic-Headphones-RP-HT161-K-Lightweight-Long-Corded/dp/B075LT8YLR/ref=sr_1_7?crid=27B0L3SFD4DKL&keywords=over+ear+headphones&qid=1550191243&s=electronics&sprefix=over+ear+%2Celectronics%2C190&sr=1-7","16.99"),
        (45,"https://www.amazon.com/Bose-QuietComfort-Acoustic-Cancelling-Headphones/dp/B00M1NEUKK/ref=sr_1_38?crid=27B0L3SFD4DKL&keywords=over+ear+headphones&qid=1550191296&s=electronics&sprefix=over+ear+%2Celectronics%2C190&sr=1-38","174")
    ]



    # *******************************************
    # RECIEVING DATA AS ARGUMENTS FROM FORM
    # -------------------------------------------

    # (WILL COME IN BLUETOOTHPREF,NOISEPREF,BASSPREF,TYPE(string as above) ,PRICE(int) )
    # Form
    queryTerm1 = "bluetooth OR \"blue tooth\""
    queryTerm1Pref = int(sys.argv[1])
    queryTerm2 = "\"noise cancel\" OR \"noise canceling\""
    queryTerm2Pref = int(sys.argv[2])
    queryTerm3 = "bass OR base"
    queryTerm3Pref = int(sys.argv[3])
    queryType = str(sys.argv[4])
    queryPrice = int(sys.argv[5])


    if(queryTerm1Pref == 0):
        queryTerm1Pref = -9
    if(queryTerm2Pref == 0):
        queryTerm2Pref = -9
    if(queryTerm3Pref == 0):
        queryTerm3Pref = -9
    
    #queryTerm1Pref = queryTerm1Pref / 3
    #queryTerm3Pref = queryTerm3Pref / 2

    # queryTerm2Pref = queryTerm2Pref * (queryTerm2Pref / 5)
    # queryTerm3Pref = queryTerm3Pref * (queryTerm3Pref / 5)


    


    # *******************************************
    # PRUNEING PRODUCT IDS TO ONLY BE THOSE THAT ARE OF DESIRED TYPE AND PRICE RANGE
    # -------------------------------------------

    prodsToCurl = pruneProdID(queryType, prodIDUrlPrice, queryPrice)
    
    # *******************************************
    # GENERATE AND PERFORM CURL COMMAND
    # -------------------------------------------

    q1Curl = generateCurlCommand(prodsToCurl, queryTerm1)
    q2Curl = generateCurlCommand(prodsToCurl, queryTerm2)
    q3Curl = generateCurlCommand(prodsToCurl, queryTerm3)

    response1 = requests.get('http://localhost:8983/solr/headphones/select', params=q1Curl)
    response2 = requests.get('http://localhost:8983/solr/headphones/select', params=q2Curl)
    response3 = requests.get('http://localhost:8983/solr/headphones/select', params=q3Curl)
    
    solrResponse1 = response1.json() # stored as dictionary
    solrResponse2 = response2.json() # stored as dictionary
    solrResponse3 = response3.json() # stored as dictionary


    # *******************************************
    # PARSE JSONS AND AVERAGE PROD STAR
    # -------------------------------------------

    avgProdIdStarList1 = avgProdStar(solrResponse1)
    avgProdIdStarList2 = avgProdStar(solrResponse2)
    avgProdIdStarList3 = avgProdStar(solrResponse3)

    # *******************************************
    #  APPLY SCORING PER UNIQUE PROD
    # -------------------------------------------
    
    termsScoreListofList = score(avgProdIdStarList1, queryTerm1Pref, avgProdIdStarList2, queryTerm2Pref, avgProdIdStarList3, queryTerm3Pref)

    # *******************************************
    # AVERAGE PROD SCORES AND UPDATE TOP TERMS AND TOP PRODUCT
    # -------------------------------------------

    return(toRubyString(tops(termsScoreListofList,queryTerm1Pref,queryTerm2Pref,queryTerm3Pref),prodIDUrlPrice))



if __name__ == "__main__":
    toRuby = main()
    # This functions as a return (its returning to STDOUT)
    print(toRuby)