/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   select_sort.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/18 10:52:54 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/28 13:22:39 by aisfi            ###   ########.fr       */
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
	r = i;
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

static void	move_to_min(int min, t_ctr *s)
{
	int	i;

	i = 0;
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
}

void	select_sort(t_ctr *s)//valid
{
	int		min;

	while (s->a->size > 0)
	{
		min = min_rotation(s->a);
		move_to_min(min, s);
		pb(s);
	}
	while (s->b->size > 0)
		pa(s);
}
