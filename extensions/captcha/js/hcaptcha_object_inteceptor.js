var __hcaptchaInitParameters={responses:{lastSolution:null},params:{lastParams:null},challenges:{}};(function(){var a={};if(document.currentScript&&document.currentScript.dataset&&document.currentScript.dataset["parameters"]){try{a=JSON.parse(document.currentScript.dataset["parameters"])}catch(o){}}if(a.originalHcaptchaApiUrl&&a.currentHcaptchaApiUrl&&a.originalHcaptchaApiUrl!==a.currentHcaptchaApiUrl){var e=document.getElementsByTagName("script");for(var t in e){if(e[t].src===a.originalHcaptchaApiUrl){e[t].src=a.currentHcaptchaApiUrl;break}}}else{}var r=a.currentOnloadMethodName;var n=a.originalOnloadMethodName;if(r){function c(){var a;if(typeof window[r]==="function"){a=window[r]}window[r]=function(){var e=hcaptcha.render;var t=hcaptcha.execute;var r=hcaptcha.getRespKey;hcaptcha.render=function(a,t){if(t&&typeof t.callback=="function"){var r=t.callback;t.callback=function(){r.apply(this,arguments)}}var n=e.apply(this,arguments);__hcaptchaInitParameters.params.lastParams=t;__hcaptchaInitParameters.params[n]=t;return n};var n=hcaptcha.getResponse;hcaptcha.getResponse=function(a){if(typeof __hcaptchaInitParameters["responses"][a]!=="undefined"){return __hcaptchaInitParameters["responses"][a]}else if(__hcaptchaInitParameters["responses"]["lastSolution"]){return __hcaptchaInitParameters["responses"]["lastSolution"]}else if(typeof n==="function"){var e=n.apply(this,arguments);return e}};hcaptcha.execute=function(a){var e=t.apply(this,arguments);return e};hcaptcha.getRespKey=function(){var a=r.apply(this,arguments);return a};if(typeof a==="function"){a.apply(this,arguments)}}}if(!n||typeof window[r]!=="undefined"){c()}else{var i=setInterval((function(){if(typeof window[r]==="undefined"){return}clearInterval(i);c()}),1)}}window.addEventListener("message",(function(a){if(!a.data||typeof a.data.receiver=="undefined"||a.data.receiver!=="hcaptchaObjectInterceptor"){return}var e=a.data;if(e.type==="hcaptchaTaskSolution"){__hcaptchaInitParameters["responses"][e.widgetID]=e.taskSolution;__hcaptchaInitParameters["responses"]["lastSolution"]=e.taskSolution;s(e.widgetID)}else if(e.type==="hcaptchaChallengeShown"){__hcaptchaInitParameters.challenges[e.widgetID]=true;s(e.widgetID)}}));window.addEventListener("message",(function(a){if(!a.data||typeof a.data!=="string"){return}var e=null;try{e=JSON.parse(a.data)}catch(a){}if(!e){return}if(e.source!=="hcaptcha"){return}if(e.label==="challenge-ready"){__hcaptchaInitParameters.challenges[e.id]=true;s(e.id)}}));function s(e){if(!a.runExplicitInvisibleHcaptchaCallbackWhenChallengeShown||!__hcaptchaInitParameters.params[e]||!__hcaptchaInitParameters.params[e].size||__hcaptchaInitParameters.params[e].size!=="invisible"||__hcaptchaInitParameters.challenges[e]){p(e)}}function p(a){h(a);if(a&&__hcaptchaInitParameters.responses[a]&&__hcaptchaInitParameters.params[a]&&__hcaptchaInitParameters.params[a].callback){var e=__hcaptchaInitParameters.params[a].callback;var t=__hcaptchaInitParameters.responses[a];if(typeof e==="function"){e(t)}else if(typeof e==="string"&&typeof window[e]==="function"){window[e](t)}}}function h(a){if(a&&__hcaptchaInitParameters.responses[a]){var e=document.getElementById("g-recaptcha-response-"+a);var t=document.getElementById("h-captcha-response-"+a);if(e){e.value=__hcaptchaInitParameters.responses[a]}if(t){t.value=__hcaptchaInitParameters.responses[a]}}}})();