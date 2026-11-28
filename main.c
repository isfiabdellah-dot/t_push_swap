/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nguerrab <nguerrab@student.1337.ma>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/20 11:19:02 by nguerrab          #+#    #+#             */
/*   Updated: 2026/11/28 18:38:07 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "./header/push_swap.h"

static	void	find(char *av, int *c)
{
	int	i;

	i = 0;
	while (av[i])
	{
		while (av[i] == ' ')
			i++;
		if (av[i] == '-' || av[i] == '+')
			i++;
		if (av[i] >= '0' && av[i] <= '9')
		{
			(*c)++;
			while (av[i] >= '0' && av[i] <= '9')
				i++;
		}
		while (av[i] != ' ' && !(av[i] >= '0' && av[i] <= '9') && av[i])
			i++;
	}
}

static	int	inputs(int ac, char **av)
{
	int		c;
	int		i;

	c = 0;
	i = 0;
	while (i < ac)
	{
		find(av[i], &c);
		i++;
	}
	return (c);
}

int	add_to(t_ctr *s, int ac, char **av)
{
	int	c;
	int	i;

	c = 0;
	i = 0;
	while (c < ac)
	{
		if (isallnum(av[c]) == 0 || (isallnum(av[c]) && !isnum(av[c])))
		{
			stack_free(s->a);
			stack_free(s->b);
			return (0);
		}
		else
		{
			if (valid_add(av[c], s, &i) == 0)
			{
				stack_free(s->a);
				stack_free(s->b);
				return (0);
			}
		}
		c++;
	}
	return (1);
}

static	int	check_flag(int argc, char **argv, int *flag)
{
	if (ft_memcmp(argv[1], "--simple", ft_strlen(argv[1])) == 0)
		*flag = 1;
	else if (ft_memcmp(argv[1], "--medium", ft_strlen(argv[1])) == 0)
		*flag = 2;
	else if (ft_memcmp(argv[1], "--complex", ft_strlen(argv[1])) == 0)
		*flag = 3;
	else if (ft_memcmp(argv[1], "--adaptive", ft_strlen(argv[1])) == 0)
		*flag = 4;
	else
		*flag = 0;
	if (*flag == 0)
		return (inputs(argc - 1, argv + 1));
	else
		return (inputs(argc - 2, argv + 2));
}

int	main(int argc, char **argv)
{
	t_ctr	*s;
	int		flag;
	int		c;

	if (argc < 2)
		return (0);
	s = NULL;
	c = check_flag(argc, argv, &flag);
	if (flag != 0)
	{
		if (argc < 3)
			error();
	}
	if (c == 0)
		error();
	else
		s = ctr_int(c);
	if (!s)
		error();
	ifelse(flag, argc, argv, s);
	push_swap(s, flag);
	bench(s);
	stack_free(s->a);
	stack_free(s->b);
	free(s);
	return (0);
}
