<script>
    $("#id_3-date_of_application").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    $("#id_3-starting_date").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    $("#id_3-date_of_manure").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    $("#id_3-sourcing_date").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        locale: {
            format: 'YYYY-MM-DD'
        },
        maxYear: parseInt(moment().format("YYYY"),12)
    });
    $(document).ready(function() {
        
        const initialVal = $('#id_3-souce_of_input').val()
        toggleSourcingFields(initialVal)

        $('#id_3-souce_of_input').on('change', function() {
            const sourcing = $(this).find(":selected").val()
            toggleSourcingFields(sourcing)
        })
    })

    const toggleSourcingFields = (sourcing) => {
        if (sourcing === 'ON_FARM'){
            $('.on-farm-input').parent().css('display', 'block')
            $('.off-farm-input').parent().css('display', 'none')
        }
        else if (sourcing === 'OUTSOURCED'){
            $('.on-farm-input').parent().css('display', 'none')
            $('.off-farm-input').parent().css('display', 'block')
        }
        else{
            // hide both
            $('.on-farm-input').parent().css('display', 'none')
            $('.off-farm-input').parent().css('display', 'none')
        }
    }

    
</script>