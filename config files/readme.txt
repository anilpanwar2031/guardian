DEV
docker build . -f Dockerfile -t akashkapoor1985/paymentpostscrapper:pp1
docker push akashkapoor1985/paymentpostscrapper:pp1

###################################################################

PROD
docker build . -f Dockerfile -t akashkapoor1985/paymentpostscrapper:ppproduction
docker push akashkapoor1985/paymentpostscrapper:ppproduction