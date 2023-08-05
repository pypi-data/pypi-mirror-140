def cal():
    filename=""
    yenikel=[]
    ses="âaeıiîoöuüû"
    siz="zyfvtşsrpnmlkhjğgdçcbx"
    while True:
        ccc = input("_-_ : ")
        if ccc=="":
            print("Veri Girişi Yok. NO DATA ")

        else:
            soruu=ccc
            soruB=soruu.lower()
            soru=soruB.strip()
            for b in range(len(soru)):

                for y in range(len(ses)):
                    if soru[b]==ses[y]:
            
                        yenikel.append(ord(ses[y])*1881)

                for y in range(len(siz)):
                    if soru[b]==siz[y]:
            
                        yenikel.append(ord(siz[y])*1881)

            ana=yenikel
            filename=str(yenikel[0]*len(soru)-31)
            bbb=open(filename+'.txt','w', encoding="utf8")
            for jk in range(len(ana)):
    
                bbb.write(str(ana[jk])+" * ")
   

            bbb.close()
    
       
        print("Veri İşlendi Şifreniz "+str(filename)+" DONT FORGET THİS PASSWORD. ")

"""EMİRCAN KELEŞ""" 
