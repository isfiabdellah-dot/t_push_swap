/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   radix_sort_lsd.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/27 10:13:09 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/28 15:51:12 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

int	get_max(t_stack *a)
{
	int	max;
	int	i;

	i = 0;
	max = a->arr[(a->head + i) % a->capacity];
	while (i < a->size)
	{
		if (max < a->arr[(a->head + i) % a->capacity])
			max = a->arr[(a->head + i) % a->capacity];
		i++;
	}
	return (max);
}

static int	get_max_bits(int max_value)
{
	int	bits;

	bits = 0;
	while (max_value)
	{
		bits++;
		max_value = max_value >> 1;
	}
	return (bits);
}

static void	radix_u(t_ctr *s, int bit, int *rk)
{
	int	value;
	int	i;
	int	bits;

	i = 0;
	bits = get_max_bits(get_max(s->a));
	while (i < s->a->capacity)
	{
		value = ft_index(s->a->arr[s->a->head], rk, s->a);
		if ((value >> bit) & 1)
			ra(s);
		else
			pb(s);
		i++;
	}
}

void	radix_sort(t_ctr *s)
{
	int	*rk;
	int	bit;

	rk = ranking(s->a);
	if (!rk)
		error();
	bit = 0;
	while (bit < s->a->capacity)
	{
		radix_u(s, bit, rk);
		while (s->b->size > 0)
			pa(s);
		if (stack_is_sorted(s->a))
			break ;
		bit++;
	}
	free(rk);
}
