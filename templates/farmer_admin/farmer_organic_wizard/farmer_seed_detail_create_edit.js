<script>
    $("#id_1-date_of_purchase").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    

</script>