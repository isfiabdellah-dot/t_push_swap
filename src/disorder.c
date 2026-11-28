/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   disorder.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/26 14:38:21 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/28 19:03:10 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

void	disorder(t_ctr *s)
{
	float	mistakes;
	float	total_pairs;
	int		i;
	int		j;
	int		value;

	mistakes = 0;
	total_pairs = 0;
	i = 0;
	if (s->a->size < 2)
		return ;
	while (i < s->a->size)
	{
		j = i + 1;
		while (j < s->a->size)
		{
			total_pairs++;
			value = s->a->arr[(s->a->head + i) % s->a->capacity];
			if (value > s->a->arr[(s->a->head + j) % s->a->capacity])
				mistakes++;
			j++;
		}
		i++;
	}
	s->disorder = mistakes / total_pairs;
}
