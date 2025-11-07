var service1 = document.querySelector('.resp-service .service#service1');
var service2 = document.querySelector('.resp-service .service#service2');
var service3 = document.querySelector('.resp-service .service#service3');
var service4 = document.querySelector('.resp-service .service#service4');
var service5 = document.querySelector('.resp-service .service#service5');
var service6 = document.querySelector('.resp-service .service#service6');

var currentSliderResp = service1;

window.addEventListener('load', nextHandlerResp)

function nextHandlerResp() {
    if (currentSliderResp === service1) {
        service1.style.display = 'none';
        service2.style.display = 'flex';
        currentSliderResp = service2;
    } else {
        if (currentSliderResp === service2) {
            service2.style.display = 'none';
            service3.style.display = 'flex';
            currentSliderResp = service3;
        } else {
            if (currentSliderResp === service3) {
                service3.style.display = 'none';
                service4.style.display = 'flex';
                currentSliderResp = service4;
            } else {
                if (currentSliderResp === service4) {
                    service4.style.display = 'none';
                    service5.style.display = 'flex';
                    currentSliderResp = service5;
                } else {
                    if (currentSliderResp === service5) {
                        service5.style.display = 'none';
                        service6.style.display = 'flex';
                        currentSliderResp = service6;
                    } else {
                        if (currentSliderResp === service6) {
                            service6.style.display = 'none';
                            service1.style.display = 'flex';
                            currentSliderResp = service1;
                        }
                    }
                }
            }
        }
    }
}

setInterval(nextHandlerResp, 10000);
