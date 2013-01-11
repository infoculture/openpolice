 $(function() {
			var $tooltip = $('<div class="tooltip">Tooltip</div>');
			$('.bubble-chart').append($tooltip);
			$tooltip.hide();
			
			var getTooltip = function() {
				return this.getAttribute('tooltip');
			};
			
			//$(function() { if (node.description == 'undefined') desc = '';
			//else  desc = node.description;)} 

			var initTooltip = function(node, domnode) {
				domnode.setAttribute('tooltip', '<div class="tooltip-label"><h3>'+node.label+'</h3></div><br><div class="tooltip-desc"><i>'+ node.description +'</i></div><div class="tooltip-amount"><h2><span class="tooltip-rubl">e</span>&nbsp;'+node.famount+'</h2></div>');
				
				vis4.log(domnode.getAttribute('tooltip'));
				
				$(domnode).tooltip({ delay: 200, bodyHandler: getTooltip });
			};
	

            new BubbleTree({
                data: data,
                container: '.bubbletree',
                bubbleType: ['icon','icon','icon', 'donut'],
		initTooltip: initTooltip,
		maxNodesPerLevel: 12,
                bubbleStyles: {
                    'fb': {                                              //taxonomy
			'all': {                                        //name of the node/child
                            icon: 'bubbletree/styles/icons/money.svg' //icon url
                        },                        
			'natsec': {                                        //name of the node/child
                            // color: '#9900cc',                       //color of the bubble if you like to set it here
                            icon: 'bubbletree/styles/icons/defence.svg' //icon url
                        },
                        'ovd': {
                            icon: 'bubbletree/styles/icons/police2.svg'
                        },
                        'vv': {
                            icon: 'bubbletree/styles/icons/military.svg'
                        },
                        'research': {

                            icon: 'bubbletree/styles/icons/research.svg'
                        },
                        'socpol': {

                            icon: 'bubbletree/styles/icons/social-systems.svg'
                        },
                        'zhkh': {

                            icon: 'bubbletree/styles/icons/our-streets.svg'
                        },
                        'capstr': {

                            icon: 'bubbletree/styles/icons/housing.svg'
                        },
                        'soc': {

                            icon: 'bubbletree/styles/icons/family2.svg'
                        },
                        'prof': {

                            icon: 'bubbletree/styles/icons/schools.svg'
                        },
                        'retraining': {

                            icon: 'bubbletree/styles/icons/defence-research.svg'
                        },
                        'annuity': {

                            icon: 'bubbletree/styles/icons/old-age.svg'
                        },
                        'health': {

                            icon: 'bubbletree/styles/icons/health.svg'
                        },
                        'hospital': {

                            icon: 'bubbletree/styles/icons/hospital.svg'
                        },
                        'sanatorium': {

                            icon: 'bubbletree/styles/icons/housing.svg'
                        },
                        'outpatient': {

                            icon: 'bubbletree/styles/icons/ambulance.svg'
                        },
                        'epidem': {

                            icon: 'bubbletree/styles/icons/medical-supplies.svg'
                        },
                        'edu': {

                            icon: 'bubbletree/styles/icons/books.svg'
                        },
                        'hiedu': {

                            icon: 'bubbletree/styles/icons/planning.svg'
                        }
                    }
		}
            });
        });



