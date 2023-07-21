<script>

    $(document).ready(function() {
        
        var total_forms = $('#id_{{wizard_current_step}}-TOTAL_FORMS').val()

        for(var index=0; index <= total_forms-1; index++){
            var initialVal = $(`#id_{{wizard_current_step}}-${index}-{{trigger_field_name}}`).val()
            toggleSourcingFields(initialVal, `form_${index}`)

            $(`#id_{{wizard_current_step}}-${index}-{{trigger_field_name}}`).on('change', function(element) {
                var new_index = element.currentTarget.id.split('-')[1]
                let sourcing = $(this).find(":selected").val()
                toggleSourcingFields(sourcing, `form_${new_index}`)
            })

        }

        $('#id_{{wizard_current_step}}-TOTAL_FORMS').on('change', function() {
            var total_forms = $('#id_{{wizard_current_step}}-TOTAL_FORMS').val()
            for(var index=0; index <= total_forms-1; index++){
                var initialVal = $(`#id_{{wizard_current_step}}-${index}-{{trigger_field_name}}`).val()
                toggleSourcingFields(initialVal, `form_${index}`)
    
                $(`#id_{{wizard_current_step}}-${index}-{{trigger_field_name}}`).on('change', function(element) {
                    var new_index = element.currentTarget.id.split('-')[1]
                    let sourcing = $(this).find(":selected").val()
                    toggleSourcingFields(sourcing, `form_${new_index}`)
                })
    
            }
        }) 
        
    })

    const toggleSourcingFields = (sourcing, form_id) => {
        console.log('sourcing', sourcing, form_id)
        if (sourcing === 'ON_FARM'){
            $(`#${form_id}`).find('.on-farm-input').parent().css('display', 'block')
            $(`#${form_id}`).find('.off-farm-input').parent().css('display', 'none')
        }
        else if (sourcing === 'OUTSOURCED'){
            $(`#${form_id}`).find('.on-farm-input').parent().css('display', 'none')
            $(`#${form_id}`).find('.off-farm-input').parent().css('display', 'block')
        }
        else{
            // hide both
            $(`#${form_id}`).find('.on-farm-input').parent().css('display', 'none')
            $(`#${form_id}`).find('.off-farm-input').parent().css('display', 'none')
        }
    }

    
    
</script>