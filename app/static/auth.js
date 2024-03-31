var auth = new Vue({
    el: '#auth',
    data: {
        username: '',
        password: '',
        token: '',
        refresh_token: '',
        isLoggedIn: false,

    },
    methods: {
        register() {
            const vm = this;
            axios.post('http://127.0.0.1:8000/api/register/', {username: vm.username, password: vm.password})
                .then(response => {
                    console.log('API Response:', response);
                    console.log("User successfully registered.");
                    vm.login();
                })
                .catch(error => {
                    if (error.response && error.response.status === 400) {
                        // Display error message from backend
                        console.log(error.response.data);
                        alert(error.response.data.username[0]);  // Example: "A user with that username already exists."
                    } else {
                        // Handle other types of errors (e.g., network issues)
                        console.log('An error occurred:', error);
                    }
                });
        },
        login() {
            const vm = this;
            axios.post('http://127.0.0.1:8000/api/token/', {username: vm.username, password: vm.password})
                .then(response => {
                    console.log('API Response:', response);
                    vm.token = response.data.access;
                    vm.refresh_token = response.data.refresh;
                    localStorage.setItem('userToken', vm.token);
                    localStorage.setItem('username', vm.username);
                    vm.isLoggedIn = true;
                })
                .catch(error => {
                    console.log(error);
                });
        },
        checkLogin() {
            if (localStorage.getItem('userToken')) {
                this.isLoggedIn = true;
                this.username = localStorage.getItem('username') || '';
            }
        },
        logout() {
            localStorage.removeItem('userToken');
            localStorage.removeItem('username');
            this.isLoggedIn = false;
            this.username = '';
            this.token = '';
            this.refresh_token = '';
        },
    },
    created() {
        this.checkLogin();
    }

});
