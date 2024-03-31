new Vue({
    el: '#cart',
    data: {
        cartItem: '',
        selectedSize: '',
    },
    methods: {
        addToCart: function (id) {
            let token = localStorage.getItem('userToken');
            if (this.selectedSize) {
                axios.post('/api/cartItem/', {
                    clothes_id: id,  // Изменено с 'clothes' на 'clothes_id'
                    size: this.selectedSize
                }, {
                    headers: {
                        'Authorization': 'Bearer ' + token  // Include the token in the request headers
                    }
                })
                    .then((response) => {
                        console.log(response)
                    })
                    .catch(function (error) {
                        console.log(error);
                    });
            } else {
                alert('Please choose a size')  // Изменено сообщение об ошибке для ясности
            }
        },
        setSize: function (size) {
            this.selectedSize = size;
            console.log(this.selectedSize)
        },
        fetchData: function () {
            const params = new URLSearchParams(window.location.search);
            let cartId = params.get('id') || '';
            let query = '/api/clothes/?id=' + cartId;

            axios.get(query)
                .then((response) => { // Use arrow function here
                    console.log('API Response:', response);

                    this.cartItem = response.data.results[0];
                })
                .catch(function (error) {
                    console.log(error);
                });
        }
    },
    created: function () {
        this.fetchData();
    },
});
