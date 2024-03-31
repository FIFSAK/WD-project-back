new Vue({
    el: '#usercart',
    data: {
        userItems: [],
    },
    methods: {
        fetchData: function () {
            let token = localStorage.getItem('userToken');
            axios.get('/api/cartItem/',
                {
                    headers: {
                        'Authorization': 'Bearer ' + token  // Include the token in the request headers
                    }
                })
                .then((response) => {
                    console.log(response)
                    this.userItems = response.data.results;
                    ;
                })
                .catch(function (error) {
                    console.log(error);
                });
        },
        deleteItem: function (cartItemId) {
            let token = localStorage.getItem('userToken');
            axios.delete('/api/cartItem/' + cartItemId + '/', {  // Include the CartItem ID in the URL
                headers: {
                    'Authorization': 'Bearer ' + token  // Include the token in the request headers
                }
            })
                .then((response) => {
                    console.log(response);
                    location.reload()
                    // Update the userItems array as needed
                })
                .catch(function (error) {
                    console.log(error);
                });
        },
    },
    created: function () {
        this.fetchData();
    },
});
