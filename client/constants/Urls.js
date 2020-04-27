const MainURL = 'https://cureona.herokuapp.com/';

export default {
    routes: {
        login: MainURL + 'Login',
        register: MainURL + 'Registration',
        makeAnAppointment: MainURL + 'GetQueue',
        avilableQueues: MainURL + 'AvailableQueues',
        businessSettings: MainURL + 'businessSettings',
        registerBusiness: MainURL + 'RegisterBusiness',
    }
}