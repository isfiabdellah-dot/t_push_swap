/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   disorder.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/26 14:38:21 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/28 14:02:35 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "./header/push_swap.h"

float	disorder(t_stack *a)
{
	float	mistakes;
	float	total_pairs;
	int		i;
	int		j;
	int		value;

	mistakes = 0;
	total_pairs = 0;
	i = 0;
	if (a->size < 2)
		return (0);
	while (i < a->size)
	{
		j = i + 1;
		while (j < a->size)
		{
			total_pairs++;
			value = a->arr[(a->head + i) % a->capacity];
			if (value > a->arr[(a->head + j) % a->capacity])
				mistakes++;
			j++;
		}
		i++;
	}
	return (mistakes / total_pairs);
}
