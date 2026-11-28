/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   select_sort.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/18 10:52:54 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/27 15:17:59 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

static int	min_rotation(t_stack *s)
{
	int	min;
	int	index;
	int	i;
	int	r;

	i = 0;
	min = s->arr[s->head];
	r = s->head;
	while (i < s->size)
	{
		index = (s->head + i) % s->capacity;
		if (s->arr[index] < min)
		{
			min = s->arr[index];
			r = i;
		}
		i++;
	}
	return (r);
}

void	select_sort(t_ctr *s)//valid
{
	int		i;
	int		min;
	int		s1;
	int		s2;

	while (s->a->size > 0)
	{
		i = 0;
		min = min_rotation(s->a);
		if (min > s->a->size / 2)
		{
			while (i < s->a->size - min)
			{
				rra(s);
				i++;
			}
		}
		else
		{
			while (i < min)
			{
				ra(s);
				i++;
			}
		}
		pb(s);
	}
	while (s->b->size > 0)
		pa(s);
}

