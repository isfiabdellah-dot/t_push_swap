/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   chunk_sort.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nguerrab <nguerrab@student.1337.ma>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/24 19:52:55 by nguerrab          #+#    #+#             */
/*   Updated: 2026/11/28 13:37:56 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

static	void	sort_b(t_ctr *s)
{
	int	idx;

	while (s->b->size > 0)
	{
		idx = (fft_max(s->b) - s->b->head + s->b->capacity) % s->b->capacity;
		if (idx <= s->b->size / 2)
		{
			while (idx-- > 0)
				rb(s);
		}
		else
		{
			idx = s->b->size - idx;
			while (idx-- > 0)
				rrb(s);
		}
		pa(s);
	}
}

static	int	push_chunk(t_ctr *s, int min, int max, int *rk)
{
	int	r;
	int	inx;

	r = 0;
	while (r < max - min + 1)
	{
		inx = ft_index(s->a->arr[s->a->head], rk, s->a);
		if (inx >= min && inx <= max)
		{
			pb(s);
			r++;
		}
		else
			ra(s);
		if (s->b->size == 0 && stack_is_sorted(s->a))
			return (1);
	}
	return (0);
}

static	int	chunk_while(t_ctr *s, int *rk, int n, int k)
{
	int	i;
	int	min;
	int	max;

	i = 0;
	while (i < k)
	{
		min = i * n;
		max = min + n - 1;
		if (max > s->a->capacity - 1)
			max = s->a->capacity - 1;
		if (push_chunk(s, min, max, rk) == 1)
			return (1);
		i++;
	}
	return (0);
}

void	chunk_sort(t_ctr *s)
{
	int	*rk;
	int	k;
	int	n;

	if (stack_is_sorted(s->a))
		return ;
	rk = ranking(s->a);
	if (!rk)
		error();
	k = sqre(s->a->size);
	n = (s->a->size + k - 1) / k;
	if (chunk_while(s, rk, n, k))
	{
		free(rk);
		return ;
	}
	sort_b(s);
	free(rk);
}
